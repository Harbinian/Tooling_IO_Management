# -*- coding: utf-8 -*-
"""
消息队列管理 - 文件系统-based 消息队列
管理 pending/、inflight/、results/ 三个目录
"""

import json
import uuid
import shutil
import tempfile
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime


QUEUE_BASE = Path(__file__).parent / "queue"
PENDING_DIR = QUEUE_BASE / "pending"
INFLIGHT_DIR = QUEUE_BASE / "inflight"
RESULTS_DIR = QUEUE_BASE / "results"


def _atomic_write(path: Path, data: dict) -> None:
    """
    原子写入 JSON 文件：先写临时文件，成功后 replace

    Args:
        path: 目标文件路径
        data: 要写入的字典数据
    """
    temp = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        dir=path.parent,
        delete=False,
        encoding='utf-8'
    )
    try:
        json.dump(data, temp, ensure_ascii=False, indent=2)
        temp.close()
        shutil.move(temp.name, str(path))
    except Exception:
        Path(temp.name).unlink(missing_ok=True)
        raise


def _safe_json_read(path: Path) -> Optional[dict]:
    """
    安全读取 JSON 文件，忽略损坏文件

    Args:
        path: 文件路径

    Returns:
        解析后的字典，或 None（文件损坏/不存在）
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError):
        return None


@dataclass
class FeishuInfo:
    """飞书路由信息"""
    chat_id: str
    open_id: str
    message_id: str


@dataclass
class PendingMessage:
    """待处理消息"""
    id: str
    content: str
    received_at: str
    status: str
    feishu: dict

    def to_inflight(self, started_at: str) -> "InflightMessage":
        """转换为执行中消息"""
        return InflightMessage(
            id=self.id,
            content=self.content,
            received_at=self.received_at,
            started_at=started_at,
            status="running",
            progress="",
            progress_seq=0,
            progress_sent_seq=0,
            confirm_notice_sent=False,
            feishu=self.feishu
        )


@dataclass
class InflightMessage:
    """执行中消息"""
    id: str
    content: str
    received_at: str
    started_at: str
    status: str
    progress: str
    progress_seq: int
    progress_sent_seq: int
    confirm_notice_sent: bool
    feishu: dict


@dataclass
class ResultMessage:
    """结果消息"""
    id: str
    status: str
    result: str
    completed_at: str
    content: str
    feishu: dict


class MessageQueue:
    """消息队列管理器"""

    def __init__(self):
        """初始化队列目录"""
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        INFLIGHT_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def enqueue(self, content: str, feishu_info: dict) -> str:
        """
        将消息写入 pending/ 目录

        Args:
            content: 消息内容
            feishu_info: 飞书路由信息（chat_id, open_id, message_id）

        Returns:
            消息 uuid
        """
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        msg = {
            "id": msg_id,
            "content": content,
            "received_at": now,
            "status": "pending",
            "feishu": feishu_info
        }
        path = PENDING_DIR / f"{msg_id}.json"
        _atomic_write(path, msg)
        return msg_id

    def claim_next(self) -> Optional[InflightMessage]:
        """
        取出最早的 pending 消息，移动到 inflight/，状态设为 running

        Returns:
            InflightMessage 对象，或 None
        """
        # 按修改时间排序，取最早的文件
        pending_files = sorted(
            PENDING_DIR.glob("*.json"),
            key=lambda p: p.stat().st_mtime
        )
        if not pending_files:
            return None

        file_path = pending_files[0]
        data = _safe_json_read(file_path)
        if data is None:
            file_path.unlink()
            return self.claim_next()
        msg = PendingMessage(**data)

        # 移动到 inflight/
        now = datetime.utcnow().isoformat() + "Z"
        inflight = msg.to_inflight(now)
        inflight_path = INFLIGHT_DIR / f"{inflight.id}.json"
        _atomic_write(inflight_path, asdict(inflight))

        # 删除 pending 文件
        file_path.unlink()
        return inflight

    def update_progress(self, uuid: str, progress: str) -> None:
        """
        更新 inflight/ 中记录的 progress 字段，并递增 progress_seq

        Args:
            uuid: 消息 ID
            progress: 进度描述
        """
        path = INFLIGHT_DIR / f"{uuid}.json"
        if not path.exists():
            return

        data = _safe_json_read(path)
        if data is None:
            return
        data["progress"] = progress
        data["progress_seq"] = data.get("progress_seq", 0) + 1
        _atomic_write(path, data)

    def update_status(self, uuid: str, status: str) -> None:
        """
        更新 inflight/ 中记录的状态

        Args:
            uuid: 消息 ID
            status: 新状态（如 awaiting_confirm）
        """
        path = INFLIGHT_DIR / f"{uuid}.json"
        if not path.exists():
            return

        data = _safe_json_read(path)
        if data is None:
            return
        data["status"] = status
        _atomic_write(path, data)

    def get_inflight_progress_updates(self) -> List[InflightMessage]:
        """
        获取 status=running 且 progress_seq > progress_sent_seq 的记录

        Returns:
            需要推送进度更新的消息列表
        """
        results = []
        for path in INFLIGHT_DIR.glob("*.json"):
            data = _safe_json_read(path)
            if data is not None and data.get("status") == "running" and data.get("progress_seq", 0) > data.get("progress_sent_seq", 0):
                results.append(InflightMessage(**data))
        return results

    def mark_progress_sent(self, uuid: str, progress_seq: int) -> None:
        """
        进度推送后更新 progress_sent_seq

        Args:
            uuid: 消息 ID
            progress_seq: 已推送的最新 progress_seq
        """
        path = INFLIGHT_DIR / f"{uuid}.json"
        if not path.exists():
            return

        data = _safe_json_read(path)
        if data is None:
            return
        data["progress_sent_seq"] = progress_seq
        _atomic_write(path, data)

    def get_inflight_awaiting_confirm(self) -> List[InflightMessage]:
        """
        获取 status=awaiting_confirm 且 confirm_notice_sent=false 的记录

        Returns:
            需要推送"等待本地确认"提示的消息列表
        """
        results = []
        for path in INFLIGHT_DIR.glob("*.json"):
            data = _safe_json_read(path)
            if data is not None and data.get("status") == "awaiting_confirm" and not data.get("confirm_notice_sent", False):
                results.append(InflightMessage(**data))
        return results

    def mark_confirm_notice_sent(self, uuid: str) -> None:
        """
        标记"等待本地确认"提示已推送

        Args:
            uuid: 消息 ID
        """
        path = INFLIGHT_DIR / f"{uuid}.json"
        if not path.exists():
            return

        data = _safe_json_read(path)
        if data is None:
            return
        data["confirm_notice_sent"] = True
        _atomic_write(path, data)

    def write_result(self, uuid: str, status: str, result: str, feishu_info: dict, content: str) -> None:
        """
        写入 results/ 目录

        Args:
            uuid: 消息 ID
            status: 结果状态（completed/failed/cancelled）
            result: 执行结果文本
            feishu_info: 飞书路由信息
            content: 原始指令内容
        """
        msg = {
            "id": uuid,
            "status": status,
            "result": result,
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "content": content,
            "feishu": feishu_info
        }
        path = RESULTS_DIR / f"{uuid}.json"
        _atomic_write(path, msg)

    def get_pending_results(self) -> List[ResultMessage]:
        """
        获取 results/ 中所有待推送结果

        Returns:
            结果消息列表
        """
        results = []
        for path in RESULTS_DIR.glob("*.json"):
            data = _safe_json_read(path)
            if data is not None:
                results.append(ResultMessage(**data))
        return results

    def mark_result_sent(self, uuid: str) -> None:
        """
        推送后删除 results/ 文件

        Args:
            uuid: 消息 ID
        """
        path = RESULTS_DIR / f"{uuid}.json"
        if path.exists():
            path.unlink()

    def remove_inflight(self, uuid: str) -> None:
        """
        最终完成后删除 inflight/ 记录

        Args:
            uuid: 消息 ID
        """
        path = INFLIGHT_DIR / f"{uuid}.json"
        if path.exists():
            path.unlink()
