# -*- coding: utf-8 -*-
"""
CLI 轮询入口 - 轮询消息队列并执行指令
"""

import re
import sys
import time
import signal
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.feishu_bridge.feishu_queue import MessageQueue, InflightMessage
from scripts.feishu_bridge.parser import CommandParser, ParsedCommand, CommandType


class FeishuBridgeCLI:
    """飞书指令桥接 CLI"""

    def __init__(self, poll_interval: int = 5):
        """
        初始化 CLI

        Args:
            poll_interval: 轮询间隔（秒）
        """
        self.queue = MessageQueue()
        self.poll_interval = poll_interval
        self.running = True

        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理退出信号"""
        print("\n收到退出信号，正在停止...")
        self.running = False

    def poll_and_execute(self):
        """轮询队列并执行任务"""
        print("Feishu Command Bridge CLI 已启动")
        print(f"轮询间隔: {self.poll_interval} 秒")
        print("-" * 40)

        while self.running:
            try:
                # 1. 检查是否有待处理消息
                inflight = self.queue.claim_next()
                if inflight:
                    self._process_message(inflight)

                # 如果没有新消息，继续等待
                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                print("\n用户中断，正在停止...")
                self.running = False
            except Exception as e:
                print(f"轮询异常: {e}")
                time.sleep(self.poll_interval)

        print("CLI 已停止")

    def _process_message(self, inflight: InflightMessage):
        """
        处理单条消息

        Args:
            inflight: 执行中的消息
        """
        print(f"\n[{inflight.id[:8]}] 收到指令: {inflight.content[:80]}")

        # 解析指令
        command = CommandParser.parse(inflight.content)

        # 判断是否需要确认
        if CommandParser.requires_confirmation(command):
            # 更新状态为等待确认
            self.queue.update_status(inflight.id, "awaiting_confirm")
            print(f"[{inflight.id[:8]}] 等待本地确认...")
            self._wait_for_confirmation(inflight, command)
        else:
            # 直接执行
            self._execute_command(inflight, command)

    def _wait_for_confirmation(self, inflight: InflightMessage, command: ParsedCommand):
        """
        等待用户在 CLI 本地确认

        Args:
            inflight: 执行中的消息
            command: 解析后的指令
        """
        print("-" * 40)
        print(f"指令: {command.raw_content}")
        print("-" * 40)
        print("是否确认执行? (y/n): ", end="", flush=True)

        try:
            user_input = input().strip().lower()
        except EOFError:
            print("n")
            user_input = "n"

        if user_input == "y":
            print("已确认，正在执行...")
            self._execute_command(inflight, command)
        else:
            print("已取消")
            self.queue.write_result(
                inflight.id,
                "cancelled",
                "用户取消执行",
                inflight.feishu,
                inflight.content
            )
            self.queue.remove_inflight(inflight.id)

    def _execute_command(self, inflight: InflightMessage, command: ParsedCommand):
        """
        执行指令

        Args:
            inflight: 执行中的消息
            command: 解析后的指令
        """
        # 更新状态为 running
        self.queue.update_status(inflight.id, "running")

        try:
            if command.command_type == CommandType.STATUS:
                result = self._do_status(command)
            elif command.command_type == CommandType.HELP:
                result = self._do_help(command)
            elif command.command_type == CommandType.SKILL_CALL:
                result = self._do_skill_call(inflight.id, command)
            elif command.command_type == CommandType.DIRECT_EXEC:
                result = self._do_direct_exec(inflight.id, command)
            else:
                result = f"未知指令类型: {command.command_type}"

            # 写入结果
            self.queue.write_result(
                inflight.id,
                "completed",
                result,
                inflight.feishu,
                inflight.content
            )
            print(f"[{inflight.id[:8]}] 执行完成")

        except Exception as e:
            print(f"[{inflight.id[:8]}] 执行失败: {e}")
            self.queue.write_result(
                inflight.id,
                "failed",
                f"执行失败: {e}",
                inflight.feishu,
                inflight.content
            )

        # 清理 inflight
        self.queue.remove_inflight(inflight.id)

    def _update_progress(self, uuid: str, progress: str):
        """更新进度"""
        self.queue.update_progress(uuid, progress)
        print(f"  -> {progress}")

    def _do_status(self, command: ParsedCommand) -> str:
        """执行 status 命令"""
        return "✅ Feishu Command Bridge 运行中\n\n支持指令:\n- /claude status\n- /claude help\n- /claude <text>\n- /claude /skill-name <args>"

    def _do_help(self, command: ParsedCommand) -> str:
        """执行 help 命令"""
        from scripts.feishu_bridge.parser import CommandParser
        return CommandParser.get_help_text()

    def _do_skill_call(self, inflight_id: str, command: ParsedCommand) -> str:
        """执行技能调用"""
        skill_name = command.skill_name
        skill_args = command.skill_args or ""

        self._update_progress(inflight_id, f"技能调用 /{skill_name}...")

        import subprocess
        import os
        from pathlib import Path

        # 技能到脚本的映射（直接调用脚本比 claude --print 更可靠）
        SKILL_SCRIPTS = {
            "bug-sniff": "scripts/bug_sniff/cli.py",
        }

        script_path = SKILL_SCRIPTS.get(skill_name)
        if script_path:
            # 直接执行脚本
            repo_path = Path(__file__).parent.parent.parent.resolve()
            cmd = ["python", str(repo_path / script_path)]
            if skill_args:
                # 解析参数并添加到命令
                for gate in re.findall(r'G[1-6]', skill_args.upper()):
                    cmd.extend(["--gate", gate])
                if "dry-run" in skill_args.lower():
                    cmd.append("--dry-run")

            self._update_progress(inflight_id, f"执行: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=120
                )
                if result.returncode == 0:
                    output = result.stdout.strip() if result.stdout.strip() else "(无输出)"
                    return output
                else:
                    return f"脚本执行失败: {result.stderr.strip()[:200]}"
            except subprocess.TimeoutExpired:
                return "技能执行超时（120秒）"
            except FileNotFoundError:
                return "错误: 未找到 python 命令"
            except Exception as e:
                return f"技能执行异常: {str(e)[:200]}"
        else:
            # 通用 claude --print 调用（可能对某些技能不稳定）
            claude_cmd = os.path.expanduser("~/.local/bin/claude") if os.path.exists(os.path.expanduser("~/.local/bin/claude")) else "claude"
            prompt = f"execute {skill_name} skill"
            if skill_args:
                prompt += f" with args: {skill_args}"

            self._update_progress(inflight_id, f"执行: {prompt[:50]}...")

            try:
                result = subprocess.run(
                    [claude_cmd, "--print", prompt],
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=120
                )
                if result.returncode == 0:
                    output = result.stdout.strip() if result.stdout.strip() else "(无输出)"
                    return output
                else:
                    return f"技能执行失败: {result.stderr.strip()[:200]}"
            except subprocess.TimeoutExpired:
                return "技能执行超时（120秒）"
            except FileNotFoundError:
                return "错误: 未找到 claude 命令"
            except Exception as e:
                return f"技能执行异常: {str(e)[:200]}"

    def _do_direct_exec(self, inflight_id: str, command: ParsedCommand) -> str:
        """执行直接指令"""
        direct_cmd = command.direct_command

        self._update_progress(inflight_id, f"执行: {direct_cmd[:50]}")

        import subprocess

        try:
            result = subprocess.run(
                ["claude", "--print", f"{direct_cmd}"],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                encoding='utf-8',
                errors='replace',
                timeout=300
            )
            output = result.stdout if result.returncode == 0 else f"错误: {result.stderr}"
            return output
        except subprocess.TimeoutExpired:
            return "指令执行超时（5分钟）"
        except FileNotFoundError:
            return "错误: 未找到 claude 命令"
        except Exception as e:
            return f"执行异常: {e}"


def main():
    """CLI 入口"""
    import argparse
    parser = argparse.ArgumentParser(description="Feishu Command Bridge CLI")
    parser.add_argument("--poll-interval", type=int, default=5, help="轮询间隔（秒）")
    args = parser.parse_args()

    cli = FeishuBridgeCLI(poll_interval=args.poll_interval)
    cli.poll_and_execute()


if __name__ == "__main__":
    main()
