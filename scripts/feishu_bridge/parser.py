# -*- coding: utf-8 -*-
"""
指令解析器 - 解析 /claude 指令
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CommandType(Enum):
    """指令类型"""
    DIRECT_EXEC = "direct_exec"
    SKILL_CALL = "skill_call"
    STATUS = "status"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """解析后的指令"""
    command_type: CommandType
    raw_content: str
    skill_name: Optional[str] = None
    skill_args: Optional[str] = None
    direct_command: Optional[str] = None


# 需要本地确认的命令模式（可能产生副作用）
CONFIRMATION_REQUIRED_PATTERNS = [
    r"^scan\s+gates",
    r"^fix\s+",
    r"^commit\s+",
    r"^push\s+",
    r"^/\w+\s+",  # 技能调用
]


class CommandParser:
    """指令解析器"""

    @staticmethod
    def parse(text: str) -> ParsedCommand:
        """
        解析 /claude 指令内容（去掉 /claude 前缀）

        Args:
            text: 原始消息文本（已去除 /claude 前缀）

        Returns:
            ParsedCommand 对象
        """
        text = text.strip()

        # 移除开头的 /claude
        if text.lower().startswith("/claude"):
            text = text[7:].strip()

        if not text:
            return ParsedCommand(
                command_type=CommandType.UNKNOWN,
                raw_content=text
            )

        # 状态命令
        if text.lower() == "status":
            return ParsedCommand(
                command_type=CommandType.STATUS,
                raw_content=text
            )

        # 帮助命令
        if text.lower() == "help":
            return ParsedCommand(
                command_type=CommandType.HELP,
                raw_content=text
            )

        # 技能调用：/skill-name <args>
        skill_match = re.match(r"^/([a-z0-9-]+)\s*(.*)$", text, re.IGNORECASE)
        if skill_match:
            skill_name = skill_match.group(1)
            skill_args = skill_match.group(2).strip()
            return ParsedCommand(
                command_type=CommandType.SKILL_CALL,
                raw_content=text,
                skill_name=skill_name,
                skill_args=skill_args
            )

        # 直接执行
        return ParsedCommand(
            command_type=CommandType.DIRECT_EXEC,
            raw_content=text,
            direct_command=text
        )

    @staticmethod
    def requires_confirmation(command: ParsedCommand) -> bool:
        """
        判断指令是否需要 CLI 本地确认

        Args:
            command: 解析后的指令

        Returns:
            是否需要确认
        """
        if command.command_type in (CommandType.STATUS, CommandType.HELP):
            return False

        if command.command_type == CommandType.SKILL_CALL:
            # 技能调用直接执行（远程场景下无法在 CLI 本地确认）
            return False

        if command.command_type == CommandType.DIRECT_EXEC:
            # 检查是否匹配需要确认的模式
            for pattern in CONFIRMATION_REQUIRED_PATTERNS:
                if re.search(pattern, command.direct_command or "", re.IGNORECASE):
                    return True

        return False

    @staticmethod
    def get_help_text() -> str:
        """返回帮助文本"""
        return """**Claude Code 指令帮助**

支持以下指令：

`/claude <text>` - 直接执行任意指令
`/claude /skill-name <args>` - 调用其他技能
`/claude status` - 查看服务状态
`/claude help` - 显示此帮助

**示例：**
`/claude scan gates G1 G2` - 执行 G1 G2 扫描
`/claude /bug-sniff G1` - 调用 bug-sniff 技能
`/claude status` - 查看状态

**确认流程：**
- 简单查询（status/help）直接执行
- 复杂操作（scan/fix/技能调用）需要本地确认
- 飞书会收到实时进度更新"""
