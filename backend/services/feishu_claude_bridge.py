from __future__ import annotations

import json
import logging
import os
import re
import shlex
import subprocess
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import (
        CreateMessageRequest,
        CreateMessageRequestBody,
        P2ImMessageReceiveV1,
    )
except ImportError:  # pragma: no cover - exercised only when dependency is missing
    lark = None
    CreateMessageRequest = None
    CreateMessageRequestBody = None
    P2ImMessageReceiveV1 = Any


LOGGER = logging.getLogger(__name__)
SESSION_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "tooling-io-management/feishu-claude-bridge")
DEFAULT_RESULT_CHUNK_SIZE = 1500
DEFAULT_TIMEOUT_SECONDS = 900
DEFAULT_MAX_WORKERS = 2


def _optional_project_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        from config import settings as project_settings  # type: ignore
    except Exception:
        return os.getenv(name, default)
    return getattr(project_settings, name, os.getenv(name, default))


def _parse_csv(value: Optional[str]) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def extract_message_text(content: str) -> str:
    if not content:
        return ""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return content.strip()

    if isinstance(payload, dict):
        text = payload.get("text")
        if isinstance(text, str):
            return text.strip()

        lines: list[str] = []
        nested_content = payload.get("content")
        if isinstance(nested_content, list):
            for block in nested_content:
                if not isinstance(block, list):
                    continue
                for item in block:
                    if isinstance(item, dict):
                        text_value = item.get("text")
                        if isinstance(text_value, str):
                            lines.append(text_value)
        if lines:
            return "".join(lines).strip()

    return content.strip()


def normalize_user_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    return normalized.strip()


def chunk_text(text: str, limit: int = DEFAULT_RESULT_CHUNK_SIZE) -> list[str]:
    if not text:
        return [""]
    if limit <= 0:
        raise ValueError("limit must be positive")

    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break

        split_at = remaining.rfind("\n", 0, limit)
        if split_at <= 0:
            split_at = limit

        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()

    return chunks


def build_session_id(chat_id: str) -> str:
    return str(uuid.uuid5(SESSION_NAMESPACE, chat_id))


@dataclass(slots=True)
class BridgeSettings:
    feishu_app_id: str
    feishu_app_secret: str
    feishu_verification_token: str = ""
    feishu_encrypt_key: str = ""
    claude_command: str = "claude"
    claude_args: list[str] = field(default_factory=list)
    workspace_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    session_store_path: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[2]
        / "logs"
        / "feishu_claude_bridge"
        / "sessions.json"
    )
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    max_workers: int = DEFAULT_MAX_WORKERS
    allowed_open_ids: set[str] = field(default_factory=set)
    allowed_chat_ids: set[str] = field(default_factory=set)
    result_chunk_size: int = DEFAULT_RESULT_CHUNK_SIZE

    @classmethod
    def from_env(cls) -> "BridgeSettings":
        app_id = _optional_project_setting("FEISHU_CLAUDE_APP_ID") or _optional_project_setting("FEISHU_APP_ID")
        app_secret = _optional_project_setting("FEISHU_CLAUDE_APP_SECRET") or _optional_project_setting(
            "FEISHU_APP_SECRET"
        )
        if not app_id or not app_secret:
            raise ValueError("FEISHU_CLAUDE_APP_ID and FEISHU_CLAUDE_APP_SECRET are required")

        raw_args = _optional_project_setting("FEISHU_CLAUDE_ARGS", "")
        workspace_root = Path(
            _optional_project_setting(
                "FEISHU_CLAUDE_WORKSPACE_ROOT",
                str(Path(__file__).resolve().parents[2]),
            )
        ).resolve()

        session_store_path = Path(
            _optional_project_setting(
                "FEISHU_CLAUDE_SESSION_STORE",
                str(workspace_root / "logs" / "feishu_claude_bridge" / "sessions.json"),
            )
        ).resolve()

        timeout_seconds = int(_optional_project_setting("FEISHU_CLAUDE_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
        max_workers = int(_optional_project_setting("FEISHU_CLAUDE_MAX_WORKERS", str(DEFAULT_MAX_WORKERS)))
        result_chunk_size = int(
            _optional_project_setting("FEISHU_CLAUDE_RESULT_CHUNK_SIZE", str(DEFAULT_RESULT_CHUNK_SIZE))
        )

        return cls(
            feishu_app_id=app_id,
            feishu_app_secret=app_secret,
            feishu_verification_token=_optional_project_setting("FEISHU_CLAUDE_VERIFICATION_TOKEN", "")
            or _optional_project_setting("FEISHU_VERIFICATION_TOKEN", ""),
            feishu_encrypt_key=_optional_project_setting("FEISHU_CLAUDE_ENCRYPT_KEY", "")
            or _optional_project_setting("FEISHU_ENCRYPT_KEY", ""),
            claude_command=_optional_project_setting("FEISHU_CLAUDE_COMMAND", "claude") or "claude",
            claude_args=shlex.split(raw_args or ""),
            workspace_root=workspace_root,
            session_store_path=session_store_path,
            timeout_seconds=timeout_seconds,
            max_workers=max_workers,
            allowed_open_ids=_parse_csv(_optional_project_setting("FEISHU_CLAUDE_ALLOWED_OPEN_IDS")),
            allowed_chat_ids=_parse_csv(_optional_project_setting("FEISHU_CLAUDE_ALLOWED_CHAT_IDS")),
            result_chunk_size=result_chunk_size,
        )


class FileSessionStore:
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._lock = threading.Lock()
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def get_or_create(self, chat_id: str) -> str:
        with self._lock:
            data = self._load()
            session_id = data.get(chat_id)
            if session_id:
                return session_id
            session_id = build_session_id(chat_id)
            data[chat_id] = session_id
            self._save(data)
            return session_id

    def reset(self, chat_id: str) -> str:
        with self._lock:
            data = self._load()
            session_id = str(uuid.uuid4())
            data[chat_id] = session_id
            self._save(data)
            return session_id

    def set(self, chat_id: str, session_id: str) -> None:
        with self._lock:
            data = self._load()
            data[chat_id] = session_id
            self._save(data)

    def peek(self, chat_id: str) -> Optional[str]:
        with self._lock:
            data = self._load()
            return data.get(chat_id)

    def _load(self) -> dict[str, str]:
        if not self._file_path.exists():
            return {}
        with self._file_path.open("r", encoding="utf-8") as handle:
            try:
                payload = json.load(handle)
            except json.JSONDecodeError:
                LOGGER.warning("Session store is malformed; resetting: %s", self._file_path)
                return {}
        if not isinstance(payload, dict):
            return {}
        return {str(key): str(value) for key, value in payload.items()}

    def _save(self, data: dict[str, str]) -> None:
        with self._file_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)


@dataclass(slots=True)
class ClaudeRunResult:
    session_id: str
    result_text: str
    raw_payload: dict[str, Any]


class ClaudeCliRunner:
    def __init__(self, settings: BridgeSettings) -> None:
        self._settings = settings

    def run(self, prompt: str, session_id: str) -> ClaudeRunResult:
        command = [
            self._settings.claude_command,
            "--session-id",
            session_id,
            "-p",
            prompt,
            "--output-format",
            "json",
        ]
        command.extend(self._settings.claude_args)

        LOGGER.info("Running Claude CLI in %s", self._settings.workspace_root)
        completed = subprocess.run(
            command,
            cwd=str(self._settings.workspace_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=self._settings.timeout_seconds,
            check=False,
        )

        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            stdout = completed.stdout.strip()
            detail = stderr or stdout or f"claude exited with code {completed.returncode}"
            raise RuntimeError(detail)

        payload = _parse_claude_output(completed.stdout)
        result_text = str(payload.get("result") or "").strip()
        resolved_session_id = str(payload.get("session_id") or session_id)
        return ClaudeRunResult(session_id=resolved_session_id, result_text=result_text, raw_payload=payload)


def _parse_claude_output(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        return {}

    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    return {"result": text}


@dataclass(slots=True)
class IncomingMessageContext:
    chat_id: str
    open_id: str
    message_id: str
    chat_type: str
    text: str


def decode_event_context(data: Any) -> Optional[IncomingMessageContext]:
    if lark is None:
        raise RuntimeError("lark-oapi is required to decode Feishu events")

    payload = json.loads(lark.JSON.marshal(data))
    event = payload.get("event") or {}
    message = event.get("message") or {}
    sender = event.get("sender") or {}
    sender_id = sender.get("sender_id") or {}

    message_type = message.get("message_type")
    if message_type != "text":
        return None

    text = normalize_user_text(extract_message_text(str(message.get("content") or "")))
    if not text:
        return None

    return IncomingMessageContext(
        chat_id=str(message.get("chat_id") or ""),
        open_id=str(sender_id.get("open_id") or ""),
        message_id=str(message.get("message_id") or ""),
        chat_type=str(message.get("chat_type") or ""),
        text=text,
    )


class FeishuClaudeBridgeService:
    def __init__(self, settings: Optional[BridgeSettings] = None) -> None:
        if lark is None:
            raise RuntimeError("Missing dependency: install lark-oapi before running the bridge")

        self.settings = settings or BridgeSettings.from_env()
        self._client = (
            lark.Client.builder()
            .app_id(self.settings.feishu_app_id)
            .app_secret(self.settings.feishu_app_secret)
            .log_level(lark.LogLevel.INFO)
            .build()
        )
        self._store = FileSessionStore(self.settings.session_store_path)
        self._runner = ClaudeCliRunner(self.settings)
        self._executor = ThreadPoolExecutor(max_workers=self.settings.max_workers, thread_name_prefix="feishu-claude")
        self._event_handler = (
            lark.EventDispatcherHandler.builder(
                self.settings.feishu_encrypt_key,
                self.settings.feishu_verification_token,
            )
            .register_p2_im_message_receive_v1(self._handle_message)
            .build()
        )

    def start(self) -> None:
        LOGGER.info("Starting Feishu long-connection bridge")
        ws_client = lark.ws.Client(
            self.settings.feishu_app_id,
            self.settings.feishu_app_secret,
            event_handler=self._event_handler,
            log_level=lark.LogLevel.INFO,
        )
        ws_client.start()

    def _handle_message(self, data: P2ImMessageReceiveV1) -> None:
        context = decode_event_context(data)
        if context is None:
            return

        if not self._is_authorized(context):
            self._send_text(context.chat_id, "当前账号或会话未在远程开发白名单内。")
            return

        command = context.text.strip()
        if command == "/help":
            self._send_text(
                context.chat_id,
                "可用命令：\n/status 查看当前会话\n/reset 重置 Claude 会话\n其余文本会直接作为 Claude 任务执行。",
            )
            return

        if command == "/status":
            session_id = self._store.peek(context.chat_id) or build_session_id(context.chat_id)
            self._send_text(
                context.chat_id,
                f"bridge=online\nworkspace={self.settings.workspace_root}\nsession_id={session_id}",
            )
            return

        if command == "/reset":
            session_id = self._store.reset(context.chat_id)
            self._send_text(context.chat_id, f"已重置会话。\nsession_id={session_id}")
            return

        session_id = self._store.get_or_create(context.chat_id)
        self._send_text(context.chat_id, f"已接收任务，开始调用 Claude。\nsession_id={session_id}")
        self._executor.submit(self._run_prompt, context.chat_id, session_id, context.text)

    def _run_prompt(self, chat_id: str, session_id: str, prompt: str) -> None:
        try:
            result = self._runner.run(prompt, session_id)
            if result.session_id != session_id:
                self._store.set(chat_id, result.session_id)
            response_text = result.result_text or "Claude 已执行完成，但没有返回文本结果。"
        except Exception as exc:  # pragma: no cover - depends on external runtime
            LOGGER.exception("Claude execution failed")
            response_text = f"Claude 执行失败：{exc}"

        for chunk in chunk_text(response_text, self.settings.result_chunk_size):
            self._send_text(chat_id, chunk)

    def _is_authorized(self, context: IncomingMessageContext) -> bool:
        if self.settings.allowed_chat_ids and context.chat_id not in self.settings.allowed_chat_ids:
            return False
        if self.settings.allowed_open_ids and context.open_id not in self.settings.allowed_open_ids:
            return False
        return True

    def _send_text(self, chat_id: str, text: str) -> None:
        if not chat_id:
            LOGGER.warning("Missing chat_id; skip outgoing message")
            return

        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(json.dumps({"text": text}, ensure_ascii=False))
                .uuid(str(uuid.uuid4()))
                .build()
            )
            .build()
        )

        response = self._client.im.v1.message.create(request)
        if not response.success():  # pragma: no cover - depends on external runtime
            LOGGER.error(
                "Failed to send Feishu message, code=%s msg=%s log_id=%s",
                response.code,
                response.msg,
                response.get_log_id(),
            )
