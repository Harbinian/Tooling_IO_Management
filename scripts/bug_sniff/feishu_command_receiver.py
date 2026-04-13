# -*- coding: utf-8 -*-
"""
飞书指令接收器 - 从飞书消息/事件中解析并执行 bug-sniff 指令
"""

import sys
import pathlib
import re
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from utils.feishu_api import FeishuBase


class CommandType(Enum):
    """指令类型"""
    SCAN_ALL = "scan_all"
    SCAN_GATES = "scan_gates"
    HELP = "help"
    STATUS = "status"
    UNKNOWN = "unknown"


@dataclass
class BugSniffCommand:
    """解析后的 bug-sniff 指令"""
    command_type: CommandType
    gates: List[str] = None  # 如 ["G1", "G2"]
    dry_run: bool = False
    raw_command: str = ""

    def __post_init__(self):
        if self.gates is None:
            self.gates = []


class FeishuCommandParser:
    """飞书指令解析器"""

    # 支持的命令模式
    PATTERNS = [
        # /bug-sniff 全量扫描
        (r'^/bug-sniff\s*$', CommandType.SCAN_ALL),
        # /bug-sniff dry-run
        (r'^/bug-sniff\s+dry-run\s*$', CommandType.SCAN_ALL),
        # /bug-sniff G1 G2 ...
        (r'^/bug-sniff\s+((?:G[1-6]\s*)+)$', CommandType.SCAN_GATES),
        # /bug-sniff help
        (r'^/bug-sniff\s+help\s*$', CommandType.HELP),
        # /bug-sniff status
        (r'^/bug-sniff\s+status\s*$', CommandType.STATUS),
    ]

    @classmethod
    def parse(cls, text: str) -> BugSniffCommand:
        """
        解析飞书消息文本为 bug-sniff 指令

        Args:
            text: 原始消息文本

        Returns:
            BugSniffCommand 对象
        """
        text = text.strip()

        for pattern, cmd_type in cls.PATTERNS:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                if cmd_type == CommandType.SCAN_ALL:
                    dry_run = 'dry-run' in text.lower()
                    return BugSniffCommand(
                        command_type=cmd_type,
                        dry_run=dry_run,
                        raw_command=text
                    )
                elif cmd_type == CommandType.SCAN_GATES:
                    gates_str = match.group(1).strip()
                    gates = re.findall(r'G[1-6]', gates_str.upper())
                    return BugSniffCommand(
                        command_type=cmd_type,
                        gates=gates,
                        raw_command=text
                    )
                else:
                    return BugSniffCommand(
                        command_type=cmd_type,
                        raw_command=text
                    )

        return BugSniffCommand(
            command_type=CommandType.UNKNOWN,
            raw_command=text
        )

    @staticmethod
    def get_help_text() -> str:
        """返回帮助文本"""
        return """**Bug Sniff 指令帮助**

支持的命令：

`/bug-sniff` - 执行全量 G1-G6 扫描
`/bug-sniff dry-run` - 干跑模式（只渲染报告不发送）
`/bug-sniff G1 G2 G3` - 只执行指定的 gate 层
`/bug-sniff help` - 显示此帮助
`/bug-sniff status` - 查看扫描服务状态

**Gate 层说明：**
- G1: 本地预提交 (UTF-8/中文SQL/占位符/敏感信息/依赖锁定)
- G2: 静态分析 (ruff/ESLint/外部表DDL)
- G3: 测试覆盖 (pytest/vitest/playwright)
- G4: 结构检查 (8D文档/HOTFIX RFC)
- G5: 归档守卫 (命名/序号/前置条件)
- G6: 技能文件 (体积/Frontmatter/triggers/depends_on)

**示例：**
`/bug-sniff G1 G2` - 只执行 G1 和 G2 检查"""


class FeishuCommandReceiver:
    """
    飞书指令接收器

    从飞书消息中接收 bug-sniff 指令并执行。
    支持两种模式：
    1. HTTP Webhook 模式：接收飞书事件回调
    2. 轮询模式：从飞书消息列表中拉取新消息
    """

    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        """
        初始化飞书指令接收器

        Args:
            app_id: 飞书应用 ID（默认从 config/settings.py 读取）
            app_secret: 飞书应用密钥（默认从 config/settings.py 读取）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self._feishu = None

    @property
    def feishu(self) -> FeishuBase:
        """延迟初始化飞书客户端"""
        if self._feishu is None:
            self._feishu = FeishuBase()
        return self._feishu

    def parse_webhook_event(self, payload: dict) -> Optional[BugSniffCommand]:
        """
        解析飞书 Webhook 事件 payload

        适用于飞书机器人 WebSocket 事件或 HTTP 回调

        Args:
            payload: 飞书事件 payload

        Returns:
            解析后的指令，或 None
        """
        try:
            # 提取消息内容
            # 飞书事件格式: { "event": { "message": { "content": "..." } } }
            message_content = None

            if "event" in payload:
                event = payload["event"]
                if isinstance(event, dict):
                    message = event.get("message", {})
                    if isinstance(message, dict):
                        message_content = message.get("content", "")
                    elif isinstance(event, str):
                        # 某些事件格式直接是消息内容
                        message_content = event

            # im.message.receive_v1 事件格式
            if not message_content and "message" in payload:
                message = payload["message"]
                if isinstance(message, dict):
                    message_content = message.get("content", "")

            if not message_content:
                return None

            # 解析指令
            return FeishuCommandParser.parse(message_content)

        except Exception as e:
            print(f"解析飞书事件失败: {e}")
            return None

    def build_reply_response(self, command: BugSniffCommand, scan_result: "ScanResult" = None) -> dict:
        """
        构建飞书回复消息

        Args:
            command: 解析后的指令
            scan_result: 扫描结果（如果有）

        Returns:
            飞书消息 payload
        """
        if command.command_type == CommandType.UNKNOWN:
            return {
                "msg_type": "text",
                "content": {
                    "text": f"未知指令: {command.raw_command}\n\n{FeishuCommandParser.get_help_text()}"
                }
            }

        if command.command_type == CommandType.HELP:
            return {
                "msg_type": "text",
                "content": {
                    "text": FeishuCommandParser.get_help_text()
                }
            }

        if command.command_type == CommandType.STATUS:
            return {
                "msg_type": "text",
                "content": {
                    "text": "✅ Bug Sniff 服务运行中\n\n可用 Gate: G1-G6\n支持指令: /bug-sniff [G1-G6...] [dry-run]"
                }
            }

        if command.command_type in (CommandType.SCAN_ALL, CommandType.SCAN_GATES):
            if scan_result is None:
                return {
                    "msg_type": "text",
                    "content": {
                        "text": "🔄 正在执行扫描..."
                    }
                }

            # 构建扫描结果消息
            status_emoji = "✅" if scan_result.is_all_pass() else "❌"
            lines = [
                f"{status_emoji} Bug Sniff 扫描完成",
                "",
                f"**总体状态**: {scan_result.overall_status()}",
                f"- ✅ PASS: {scan_result.total_pass}",
                f"- ❌ FAIL: {scan_result.total_fail}",
                f"- ⏭️ SKIP: {scan_result.total_skip}",
                f"- ⚠️ WARN: {scan_result.total_warn}",
                "",
            ]

            # 添加失败项详情
            if scan_result.total_fail > 0:
                lines.append("**失败项:**")
                for gate in scan_result.gate_results:
                    if gate.status == "FAIL":
                        lines.append(f"- {gate.gate_id} {gate.name}")
                        if gate.message:
                            lines.append(f"  {gate.message}")
                lines.append("")

            lines.append("*由 Bug Sniff 自动生成*")

            return {
                "msg_type": "text",
                "content": {
                    "text": "\n".join(lines)
                }
            }

        return {
            "msg_type": "text",
            "content": {
                "text": "不支持的指令类型"
            }
        }


# 导入 ScanResult 以便类型提示使用
from scripts.bug_sniff.gates_scanner import ScanResult