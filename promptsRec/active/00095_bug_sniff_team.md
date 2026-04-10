# Bug 嗅探技能实现

---
name: bug-sniff
executor: Claude Code
auto_invoke: false
depends_on: []
triggers:
  - /bug-sniff
rules_ref:
  - .claude/rules/07_ci_gates.md
version: 1.0.0
---

# 目的 / Purpose

实现一个 Bug 嗅探技能，通过 `/bug-sniff` 调用触发，执行 G1-G6 全量代码质量扫描，扫描完成后通过飞书 Webhook 推送报告，进程终止。

# 上下文约束 / Context Constraints

- **只读扫描**：不得修改任何文件
- **飞书 Webhook**：已知 URL `https://open.feishu.cn/open-apis/bot/v2/hook/606947c1-f692-488f-b199-3848d15f577a`
- **复用现有逻辑**：G1 检查在 `githooks/pre-commit` 中已有实现，不得重复发明
- **G1-2 修复已知**：需使用 `grep -P '[\p{Han}]'` 替代错误的 `grep -E '[\u4e00-\u9fff]'`
- **输出格式**：飞书消息卡片（markdown），每个 gate 显示 PASS/FAIL

# 与相邻技能的边界

本技能与 `incident-monitor`（事件监控）职责不同：
- `incident-monitor`：监听运行时错误和异常
- `bug-sniff`：主动巡检代码规范性问题

# 执行步骤 / Execution Steps

## Step 1: 创建技能目录和元数据

创建 `.skills/bug-sniff/SKILL.md`，包含：
- frontmatter（name, executor, auto_invoke, depends_on, triggers, rules_ref, version）
- 技能说明
- 执行步骤
- 完成标准

## Step 2: 创建扫描脚本

创建 `scripts/bug_sniff/gates_scanner.py`，封装以下检查：

### G1 检查（从 githooks/pre-commit 迁移）
- G1-1: UTF-8 BOM 检测
- G1-2: 中文 SQL 字段检测（**修复**：使用 `grep -P '[\p{Han}]'`）
- G1-3: 占位符代码检测
- G1-4: 敏感信息检测（调用 `detect-secrets`）
- G1-5: 依赖版本锁定检测

### G2 检查
- G2-1: Python 静态分析（ruff）
- G2-2: ESLint（前端）
- G2-3: 外部表 DDL 操作检测

### G3 检查
- G3-1 ~ G3-4: pytest/vitest/playwright（依赖未安装时 skip）

### G4 检查
- G4-1: 8D 文档结构检测
- G4-2: HOTFIX RFC 检测

### G5 检查
- G5-1 ~ G5-3: 归档命名/序号/前置条件检测

**注意**：G3 依赖 pytest/vitest/playwright，如未安装则该 gate 标记为 SKIP，不阻断其他检查。

## Step 3: 创建飞书通知模块

在 `scripts/bug_sniff/feishu_reporter.py` 中：
- 定义报告格式化函数（markdown 格式）
- 实现 Webhook 发送函数
- 支持分段发送（超长消息拆分成多条）

## Step 4: 创建 CLI 入口

创建 `scripts/bug_sniff/cli.py`：
- 解析命令行参数
- 依次执行 G1-G5 检查
- 汇总结果并发送到飞书

## Step 5: 测试验证

1. 运行 `python scripts/bug_sniff/cli.py`，确认无报错
2. 确认飞书收到报告卡片
3. 验证 FAIL 项包含文件路径和具体问题描述

# 完成标准 / Completion Criteria

- [ ] `/bug-sniff` 技能文件存在且 frontmatter 完整
- [ ] `scripts/bug_sniff/gates_scanner.py` 覆盖 G1-G5 所有 gate
- [ ] `scripts/bug_sniff/feishu_reporter.py` 正确发送飞书消息
- [ ] 运行 `python scripts/bug_sniff/cli.py` 无报错
- [ ] 飞书 Webhook 收到包含 PASS/FAIL 状态的报告卡片
- [ ] G1-2 使用 `grep -P '[\p{Han}]'` 无 false positive

# 关键文件参考

| 文件 | 用途 |
|------|------|
| `githooks/pre-commit` | G1 检查逻辑来源 |
| `docs/07_ci_gates.md` | G1-G6 门禁规则定义 |
| `utils/feishu_api.py` | 飞书 Webhook 发送参考 |
| `backend/database/schema/column_names.py` | 字段名常量（用于 G2-3 检测） |
