# -*- coding: utf-8 -*-
"""
飞书指令 HTTP 服务器
接收飞书 Webhook 事件并执行 bug-sniff 扫描
支持 /claude 指令桥接到 Claude Code CLI
"""

import sys
import pathlib
import time
import threading
import json
from flask import Flask, request, jsonify

# 添加项目根目录到路径
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from scripts.bug_sniff.gates_scanner import GatesScanner
from scripts.bug_sniff.feishu_reporter import FeishuReporter
from scripts.bug_sniff.feishu_command_receiver import (
    FeishuCommandReceiver,
    CommandType,
)
from scripts.feishu_bridge.queue import MessageQueue


def create_app(repo_path: str = ".", dry_run: bool = False, webhook_url: str = None, use_command_dry_run: bool = True):
    """
    创建 Flask 应用

    Args:
        repo_path: 仓库路径
        dry_run: 服务器默认干跑模式（仅在 use_command_dry_run=False 时生效）
        webhook_url: 飞书 Webhook URL（优先使用，None 则从 settings 读取）
        use_command_dry_run: 是否使用指令中的 dry_run（True=每次飞书指令控制，False=服务器固定模式）
    """
    app = Flask(__name__)

    # 确定 webhook_url：CLI 参数 > settings 配置
    if webhook_url is None:
        from config.settings import settings
        webhook_url = settings.FEISHU_WEBHOOK_URL_BUG_SNIFF or settings.FEISHU_WEBHOOK_URL

    # 存储配置
    app.config['REPO_PATH'] = repo_path
    app.config['DRY_RUN'] = dry_run
    app.config['WEBHOOK_URL'] = webhook_url
    app.config['USE_COMMAND_DRY_RUN'] = use_command_dry_run
    app.config['FEISHU_RECEIVER'] = FeishuCommandReceiver()
    app.config['MESSAGE_QUEUE'] = MessageQueue()

    # 启动后台轮询线程
    _start_background_polling(app)

    @app.route('/health', methods=['GET'])
    def health():
        """健康检查"""
        return jsonify({
            "status": "ok",
            "service": "bug-sniff-feishu-listener",
            "feishu_bridge": "enabled"
        })

    @app.route('/webhook/feishu', methods=['POST'])
    def feishu_webhook():
        """
        飞书 Webhook 回调端点

        接收飞书机器人事件，解析 bug-sniff 指令或 /claude 指令
        /claude 指令写入消息队列，由 CLI 轮询执行
        """
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"code": 1, "msg": "empty payload"}), 400

            # 提取飞书路由信息
            feishu_info = _extract_feishu_info(payload)
            if feishu_info is None:
                return jsonify({"code": 0, "msg": "no feishu info found"})

            # 提取消息内容
            message_content = _extract_message_content(payload)
            if not message_content:
                return jsonify({"code": 0, "msg": "no message content"})

            # 检测 /claude 指令
            if message_content.strip().lower().startswith("/claude"):
                return _handle_claude_command(message_content, feishu_info, app)

            # 其他指令走原有 bug-sniff 逻辑
            return _handle_bug_sniff_command(payload, message_content, app)

        except Exception as e:
            print(f"处理飞书 webhook 异常: {e}")
            return jsonify({"code": 1, "msg": str(e)}), 500

    return app


def _extract_feishu_info(payload: dict) -> dict:
    """从 payload 中提取飞书路由信息"""
    try:
        # 飞书事件格式: { "event": { "message": { ... } } }
        if "event" in payload:
            event = payload["event"]
            if isinstance(event, dict):
                message = event.get("message", {})
                if isinstance(message, dict):
                    return {
                        "chat_id": message.get("chat_id", ""),
                        "open_id": message.get("open_id", ""),
                        "message_id": message.get("message_id", "")
                    }

        # 某些事件格式
        if "message" in payload:
            message = payload["message"]
            if isinstance(message, dict):
                return {
                    "chat_id": message.get("chat_id", ""),
                    "open_id": message.get("open_id", ""),
                    "message_id": message.get("message_id", "")
                }

        return None
    except Exception:
        return None


def _extract_message_content(payload: dict) -> str:
    """从 payload 中提取消息内容"""
    try:
        if "event" in payload:
            event = payload["event"]
            if isinstance(event, dict):
                message = event.get("message", {})
                if isinstance(message, dict):
                    return message.get("content", "")

        if "message" in payload:
            message = payload["message"]
            if isinstance(message, dict):
                return message.get("content", "")

        return ""
    except Exception:
        return ""


def _handle_claude_command(message_content: str, feishu_info: dict, app) -> dict:
    """处理 /claude 指令，写入消息队列"""
    try:
        queue = app.config['MESSAGE_QUEUE']
        queue.enqueue(message_content, feishu_info)
        print(f"[Claude Bridge] 已入队: {message_content[:60]}")
        return jsonify({"code": 0, "msg": "command queued"})
    except Exception as e:
        print(f"[Claude Bridge] 入队失败: {e}")
        return jsonify({"code": 1, "msg": str(e)}), 500


def _handle_bug_sniff_command(payload: dict, message_content: str, app) -> dict:
    """处理 bug-sniff 指令（原逻辑）"""
    receiver = app.config['FEISHU_RECEIVER']
    command = receiver.parse_webhook_event(payload)

    if command is None:
        return jsonify({"code": 0, "msg": "no bug-sniff command found"})

    if app.config['USE_COMMAND_DRY_RUN']:
        request_dry_run = command.dry_run
    else:
        request_dry_run = app.config['DRY_RUN']

    if command.command_type == CommandType.UNKNOWN:
        reply = receiver.build_reply_response(command)
        send_reply(reply, app.config, dry_run=request_dry_run)
        return jsonify({"code": 0, "msg": "unknown command replied"})

    if command.command_type == CommandType.HELP:
        reply = receiver.build_reply_response(command)
        send_reply(reply, app.config, dry_run=request_dry_run)
        return jsonify({"code": 0, "msg": "help replied"})

    if command.command_type == CommandType.STATUS:
        reply = receiver.build_reply_response(command)
        send_reply(reply, app.config, dry_run=request_dry_run)
        return jsonify({"code": 0, "msg": "status replied"})

    if command.command_type == CommandType.SCAN_ALL:
        scanner = GatesScanner(repo_path=app.config['REPO_PATH'])
        results = scanner.run_all_gates()
    elif command.command_type == CommandType.SCAN_GATES:
        scanner = GatesScanner(repo_path=app.config['REPO_PATH'])
        results = run_selected_gates(scanner, command.gates)
    else:
        return jsonify({"code": 1, "msg": "unsupported command"})

    scanning_reply = receiver.build_reply_response(command, None)
    send_reply(scanning_reply, app.config, dry_run=request_dry_run)

    reply = receiver.build_reply_response(command, results)

    if results.total_fail > 0:
        reporter = FeishuReporter(
            webhook_url=app.config['WEBHOOK_URL'],
            dry_run=request_dry_run
        )
        reporter.send_segments(results)
    else:
        send_reply(reply, app.config, dry_run=request_dry_run)

    return jsonify({"code": 0, "msg": "scan completed"})


def _start_background_polling(app):
    """启动后台轮询线程（进度推送和结果推送）"""
    def poll():
        while True:
            try:
                queue = app.config.get('MESSAGE_QUEUE')
                webhook_url = app.config.get('WEBHOOK_URL')
                if queue and webhook_url:
                    _poll_progress_updates(queue, webhook_url)
                    _poll_confirm_notices(queue, webhook_url)
                    _poll_results(queue, webhook_url)
            except Exception as e:
                print(f"[Polling] 轮询异常: {e}")
            time.sleep(5)

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()


def _poll_progress_updates(queue: MessageQueue, webhook_url: str):
    """轮询进度更新并推送"""
    try:
        updates = queue.get_inflight_progress_updates()
        for inflight in updates:
            message = f"🔄 {inflight.content[:40]}...\n\n进度: {inflight.progress}"
            if _send_feishu_message(webhook_url, message):
                queue.mark_progress_sent(inflight.id, inflight.progress_seq)
    except Exception as e:
        print(f"[Polling] 进度推送异常: {e}")


def _poll_confirm_notices(queue: MessageQueue, webhook_url: str):
    """轮询等待确认通知并推送"""
    try:
        notices = queue.get_inflight_awaiting_confirm()
        for inflight in notices:
            message = f"⏳ 等待本地确认...\n\n指令: {inflight.content[:60]}\n\n请在 Claude Code CLI 中确认执行"
            if _send_feishu_message(webhook_url, message):
                queue.mark_confirm_notice_sent(inflight.id)
    except Exception as e:
        print(f"[Polling] 确认通知推送异常: {e}")


def _poll_results(queue: MessageQueue, webhook_url: str):
    """轮询结果并推送"""
    try:
        results = queue.get_pending_results()
        for result in results:
            if result.status == "completed":
                message = f"✅ 执行完成\n\n指令: {result.content[:60]}\n\n{result.result[:500]}"
            elif result.status == "failed":
                message = f"❌ 执行失败\n\n指令: {result.content[:60]}\n\n{result.result[:500]}"
            elif result.status == "cancelled":
                message = f"⚠️ 已取消\n\n指令: {result.content[:60]}\n\n{result.result}"
            else:
                message = f"📋 状态: {result.status}\n\n{result.result[:500]}"

            if _send_feishu_message(webhook_url, message):
                queue.mark_result_sent(result.id)
    except Exception as e:
        print(f"[Polling] 结果推送异常: {e}")


def _send_feishu_message(webhook_url: str, message: str) -> bool:
    """
    发送飞书消息

    Returns:
        True if sent successfully, False otherwise
    """
    if not webhook_url:
        print("[Feishu] Webhook URL 未配置，跳过推送")
        return False

    import requests
    try:
        payload = {
            "msg_type": "text",
            "content": {"text": message}
        }
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"[Feishu] 消息推送成功")
                return True
            else:
                print(f"[Feishu] 飞书返回错误: code={result.get('code')}, msg={result.get('msg')}")
                return False
        else:
            print(f"[Feishu] HTTP 错误: status={response.status_code}")
            return False
    except Exception as e:
        print(f"[Feishu] 消息推送失败: {e}")
        return False


def run_selected_gates(scanner: GatesScanner, gates: list) -> "ScanResult":
    """执行选定的 gate 层"""
    from scripts.bug_sniff.gates_scanner import ScanResult

    results = ScanResult(repo_path=str(scanner.repo_path))

    gate_map = {
        "G1": [
            scanner.check_g1_1_utf8_bom,
            scanner.check_g1_2_chinese_sql,
            scanner.check_g1_3_placeholder_code,
            scanner.check_g1_4_secrets,
            scanner.check_g1_5_dependency_pinning,
        ],
        "G2": [
            scanner.check_g2_1_ruff,
            scanner.check_g2_2_eslint,
            scanner.check_g2_3_external_ddl,
        ],
        "G3": [
            scanner.check_g3_1_pytest_coverage,
            scanner.check_g3_2_integration_coverage,
            scanner.check_g3_3_vitest,
            scanner.check_g3_4_playwright,
        ],
        "G4": [
            scanner.check_g4_1_8d_structure,
            scanner.check_g4_2_hotfix_rfc,
        ],
        "G5": [
            scanner.check_g5_1_archive_naming,
            scanner.check_g5_2_exec_sequence,
            scanner.check_g5_3_archive_precondition,
        ],
        "G6": [
            scanner.check_g6_1_skill_size,
            scanner.check_g6_2_frontmatter,
            scanner.check_g6_3_trigger_uniqueness,
            scanner.check_g6_4_dependency_exists,
            scanner.check_g6_5_meta_skill,
        ],
    }

    for layer in gates:
        if layer in gate_map:
            for check_func in gate_map[layer]:
                results.add(check_func())

    return results


def send_reply(reply: dict, config: dict, dry_run: bool = None):
    """发送回复到飞书

    Args:
        reply: 飞书消息 payload
        config: Flask 应用配置
        dry_run: 干跑模式（True=只打印不发送），如果为 None 则使用 config['DRY_RUN']
    """
    # 如果未指定 dry_run，使用配置中的默认值
    if dry_run is None:
        dry_run = config.get('DRY_RUN', False)

    if dry_run:
        print(f"[DRY RUN] 飞书回复: {reply}")
        return

    webhook_url = config.get('WEBHOOK_URL')
    if not webhook_url:
        # 如果没有配置 webhook，只打印
        print(f"[DEBUG] 无 Webhook URL，回复内容: {reply}")
        return

    import requests
    try:
        response = requests.post(
            webhook_url,
            json=reply,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("飞书回复发送成功")
            else:
                print(f"飞书回复发送失败: {result.get('msg')}")
        else:
            print(f"飞书回复请求失败: {response.status_code}")
    except Exception as e:
        print(f"飞书回复发送异常: {e}")


# 直接运行时启动服务器
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", default=".")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--webhook-url", default=None)
    args = parser.parse_args()

    app = create_app(
        repo_path=args.repo_path,
        dry_run=args.dry_run,
        webhook_url=args.webhook_url,
        use_command_dry_run=True  # 默认：每次飞书指令控制是否发送
    )
    print("================================")
    print("飞书指令监听服务已启动")
    print("监听端口: 8152")
    print("Webhook 路径: http://localhost:8152/webhook/feishu")
    print("健康检查: http://localhost:8152/health")
    print("================================")
    print("Bug Sniff 指令: /bug-sniff [G1-G6...] [dry-run]")
    print("Claude 指令桥接: /claude <指令>")
    print("================================")
    print(f"dry_run 模式: 由每次飞书指令指定（use_command_dry_run=True）")
    print(f"如需固定 dry_run 模式，请使用 --dry-run 参数")
    app.run(host="0.0.0.0", port=8152, debug=False)