# -*- coding: utf-8 -*-
"""
飞书报告器 - 格式化并发送扫描结果到飞书
"""

import sys
import pathlib

# 添加项目根目录到路径
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from dataclasses import dataclass
from typing import Optional
from scripts.bug_sniff.gates_scanner import ScanResult


class FeishuReporter:
    """飞书报告发送器"""

    def __init__(self, webhook_url: Optional[str] = None, dry_run: bool = False):
        """
        初始化飞书报告器

        Args:
            webhook_url: 飞书 Webhook URL（如果为 None，从 config/settings.py 读取）
            dry_run: True 则只渲染不发送
        """
        self.dry_run = dry_run
        self.webhook_url = webhook_url or self._get_webhook_url()

    def _get_webhook_url(self) -> str:
        """从 config/settings.py 读取飞书配置（优先使用 bug_sniff 专用配置）"""
        try:
            from config.settings import settings
            # 优先使用 bug_sniff 专用配置
            if hasattr(settings, 'FEISHU_WEBHOOK_URL_BUG_SNIFF') and settings.FEISHU_WEBHOOK_URL_BUG_SNIFF:
                return settings.FEISHU_WEBHOOK_URL_BUG_SNIFF
            return settings.FEISHU_WEBHOOK_URL or ""
        except ImportError:
            return ""

    def format_report(self, result: ScanResult) -> str:
        """
        格式化扫描结果为 Markdown 报告

        Args:
            result: 扫描结果对象

        Returns:
            Markdown 格式的报告字符串
        """
        status_emoji = "✅" if result.is_all_pass() else "❌"
        overall = f"{status_emoji} **{result.overall_status()}** - G1-G6 门禁扫描报告"

        lines = [
            f"# Bug Sniff 扫描报告",
            "",
            f"**仓库**: `{result.repo_path}`",
            f"**时间**: {self._get_timestamp()}",
            "",
            f"## 汇总结果",
            "",
            f"- ✅ PASS: {result.total_pass}",
            f"- ❌ FAIL: {result.total_fail}",
            f"- ⏭️ SKIP: {result.total_skip}",
            f"- ⚠️ WARN: {result.total_warn}",
            "",
            f"**总体状态**: {overall}",
            "",
            "---",
            "",
        ]

        # 按 gate 分组显示
        gates_by_layer = {
            "G1": [],
            "G2": [],
            "G3": [],
            "G4": [],
            "G5": [],
            "G6": [],
        }

        for gate in result.gate_results:
            layer = gate.gate_id.split('-')[0]
            if layer in gates_by_layer:
                gates_by_layer[layer].append(gate)

        for layer, gates in gates_by_layer.items():
            if not gates:
                continue

            lines.append(f"### {layer} 层")
            lines.append("")

            for gate in gates:
                status_icon = self._get_status_icon(gate.status)
                lines.append(f"{status_icon} **{gate.gate_id}** {gate.name}: {gate.status}")

                if gate.message:
                    lines.append(f"   - {gate.message}")

                if gate.details and gate.status in ("FAIL", "WARN"):
                    for detail in gate.details[:3]:
                        lines.append(f"   - `{detail}`")

                lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*由 Bug Sniff 自动生成*")

        return "\n".join(lines)

    def _get_status_icon(self, status: str) -> str:
        """获取状态对应的图标"""
        icons = {
            "PASS": "✅",
            "FAIL": "❌",
            "SKIP": "⏭️",
            "WARN": "⚠️",
        }
        return icons.get(status, "❓")

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def send(self, result: ScanResult) -> bool:
        """
        发送报告到飞书

        Args:
            result: 扫描结果对象

        Returns:
            发送是否成功
        """
        message = self.format_report(result)

        if self.dry_run:
            print("=== [DRY RUN] 飞书消息内容 ===")
            print(message)
            print("=== [DRY RUN] 飞书消息内容结束 ===")
            return True

        if not self.webhook_url:
            print("未配置飞书 Webhook URL，消息未发送")
            print("消息内容:")
            print(message)
            return False

        return self._send_webhook(message)

    def _send_webhook(self, message: str, msg_type: str = "text") -> bool:
        """
        发送 Webhook 消息到飞书

        Args:
            message: 消息内容
            msg_type: 消息类型 (text/markdown)

        Returns:
            发送是否成功
        """
        import requests

        try:
            payload = {
                "msg_type": msg_type,
                "content": {
                    "text": message
                }
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("飞书消息发送成功")
                    return True
                else:
                    print(f"飞书 Webhook 发送失败: {result.get('msg')}")
                    return False
            else:
                print(f"飞书 Webhook 请求失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"飞书 Webhook 发送异常: {e}")
            return False

    def send_segments(self, result: ScanResult, segment_size: int = 4000) -> bool:
        """
        发送报告到飞书（分段发送，处理超长消息）

        Args:
            result: 扫描结果对象
            segment_size: 每段最大字符数

        Returns:
            发送是否成功
        """
        message = self.format_report(result)

        if self.dry_run:
            return self.send(result)

        if len(message) <= segment_size:
            return self.send(result)

        # 分段发送
        segments = self._split_message(message, segment_size)
        print(f"消息过长 ({len(message)} 字符)，拆分为 {len(segments)} 段发送")

        success = True
        for i, segment in enumerate(segments, 1):
            print(f"发送第 {i}/{len(segments)} 段...")
            if not self._send_webhook(segment):
                success = False

        return success

    def _split_message(self, message: str, max_length: int) -> list:
        """将消息拆分为多段"""
        lines = message.split('\n')
        segments = []
        current = []

        for line in lines:
            test = '\n'.join(current + [line])
            if len(test) <= max_length:
                current.append(line)
            else:
                if current:
                    segments.append('\n'.join(current))
                current = [line]

        if current:
            segments.append('\n'.join(current))

        return segments
