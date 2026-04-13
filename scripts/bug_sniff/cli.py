# -*- coding: utf-8 -*-
"""
Bug Sniff CLI - G1-G6 全量仓库质量扫描入口
支持直接执行和飞书指令两种模式
"""

import argparse
import sys
import pathlib
import io
import json

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from scripts.bug_sniff.gates_scanner import GatesScanner
from scripts.bug_sniff.feishu_reporter import FeishuReporter
from scripts.bug_sniff.feishu_command_receiver import (
    FeishuCommandReceiver,
    FeishuCommandParser,
    CommandType,
)


def main():
    parser = argparse.ArgumentParser(
        description="Bug Sniff - G1-G6 全量仓库质量扫描",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="仓库路径 (默认: 当前目录)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只渲染报告，不发送飞书通知"
    )

    parser.add_argument(
        "--webhook-url",
        type=str,
        default=None,
        help="飞书 Webhook URL (默认从 config/settings.py 读取)"
    )

    parser.add_argument(
        "--gate",
        type=str,
        action="append",
        choices=["G1", "G2", "G3", "G4", "G5", "G6"],
        help="只执行指定的 gate 层 (默认: 全部)"
    )

    # 飞书指令模式
    parser.add_argument(
        "--feishu-listen",
        action="store_true",
        help="监听飞书指令模式（HTTP 服务）"
    )

    parser.add_argument(
        "--feishu-port",
        type=int,
        default=8152,
        help="飞书指令监听端口 (默认: 8152)"
    )

    parser.add_argument(
        "--feishu-webhook-path",
        type=str,
        default="/webhook/feishu",
        help="飞书 Webhook 回调路径 (默认: /webhook/feishu)"
    )

    # 从文件或 stdin 解析指令（用于测试）
    parser.add_argument(
        "--parse-command",
        type=str,
        default=None,
        help="解析给定的飞书命令文本并退出"
    )

    args = parser.parse_args()

    # 解析命令模式（用于测试）
    if args.parse_command:
        cmd = FeishuCommandParser.parse(args.parse_command)
        print(f"命令类型: {cmd.command_type.value}")
        print(f"Gate 层: {cmd.gates}")
        print(f"Dry-run: {cmd.dry_run}")
        print(f"原始命令: {cmd.raw_command}")
        return 0

    # 飞书监听模式
    if args.feishu_listen:
        from scripts.bug_sniff.feishu_http_server import create_app
        app = create_app(
            repo_path=args.repo_path,
            dry_run=args.dry_run,
            webhook_url=args.webhook_url,
        )
        print(f"启动飞书指令监听服务...")
        print(f"Webhook 路径: http://0.0.0.0:{args.feishu_port}{args.feishu_webhook_path}")
        print(f"按 Ctrl+C 停止")
        try:
            app.run(host="0.0.0.0", port=args.feishu_port, debug=False)
        except KeyboardInterrupt:
            print("\n服务已停止")
        return 0

    print("=" * 60)
    print("Bug Sniff - G1-G6 全量仓库质量扫描")
    print("=" * 60)
    print(f"仓库路径: {args.repo_path}")
    print(f"模式: {'DRY RUN (不发送通知)' if args.dry_run else '正常模式'}")
    print()

    # 执行扫描
    scanner = GatesScanner(repo_path=args.repo_path)

    if args.gate:
        print(f"只扫描指定 gate 层: {', '.join(args.gate)}")
        results = run_selected_gates(scanner, args.gate)
    else:
        print("执行全量 G1-G6 扫描...")
        results = scanner.run_all_gates()

    # 打印汇总
    print()
    print("=" * 60)
    print("扫描结果汇总")
    print("=" * 60)
    print(f"✅ PASS: {results.total_pass}")
    print(f"❌ FAIL: {results.total_fail}")
    print(f"⏭️ SKIP: {results.total_skip}")
    print(f"⚠️ WARN: {results.total_warn}")
    print()
    print(f"总体状态: {results.overall_status()}")
    print()

    # 打印失败项
    if results.total_fail > 0:
        print("失败项详情:")
        for gate in results.gate_results:
            if gate.status == "FAIL":
                print(f"  - {gate.gate_id} {gate.name}")
                if gate.message:
                    print(f"    {gate.message}")
        print()

    # 发送到飞书
    reporter = FeishuReporter(webhook_url=args.webhook_url, dry_run=args.dry_run)
    reporter.send(results)

    # 返回退出码
    if results.total_fail > 0:
        sys.exit(1)
    else:
        sys.exit(0)


def run_selected_gates(scanner: GatesScanner, gates: list) -> "ScanResult":
    """执行选定的 gate 层"""
    # 懒加载 ScanResult
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


if __name__ == "__main__":
    main()
