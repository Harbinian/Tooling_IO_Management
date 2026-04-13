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

实现一个 Bug 嗅探技能，通过 `/bug-sniff` 调用触发，执行 G1-G6 全量仓库质量扫描，扫描完成后汇总结果，并按配置将报告推送到飞书。

# 上下文约束 / Context Constraints

- **运行态只读**：`/bug-sniff` 执行扫描时不得修改被扫描仓库文件；实现阶段允许创建技能文件和脚本
- **飞书配置来源**：禁止在提示词、代码或测试中硬编码真实 Webhook URL；必须复用 `config/settings.py` 中现有 `FEISHU_*` 配置项或通过 CLI 参数注入测试地址
- **复用现有逻辑**：G1 检查模式、豁免规则和错误语义来源于 `githooks/pre-commit`，但扫描入口必须改为显式遍历目标仓库，不能沿用 staged-file 枚举
- **G1-2 修复已知**：如直接调用 grep，必须使用 `grep -P '[\p{Han}]'` 替代错误的 `grep -E '[\u4e00-\u9fff]'`；如改为 Python 实现，也必须保证等效且无 false positive
- **仓库路径适配**：`.claude/rules/07_ci_gates.md` 中示例脚本引用的 `prompts/active`、`prompts/archive` 必须适配为本仓库实际使用的 `promptsRec/active`、`promptsRec/archive`
- **输出格式**：飞书消息卡片（markdown），每个 gate 显示 PASS/FAIL

# 与相邻技能的边界

本技能与 `incident-monitor`（事件监控）职责不同：
- `incident-monitor`：监听运行时错误和异常
- `bug-sniff`：主动巡检代码规范性问题

# ADP 约束 / ADP Requirements

## Phase 1: PRD

- **业务场景**：维护者需要在提交前或巡检时，一次性得到仓库在 G1-G6 门禁上的客观结果
- **目标用户**：仓库维护者、提示词执行者、规则维护者
- **核心痛点**：现有 G1 只覆盖 staged 文件，G4-G6 示例路径与仓库实际结构存在偏差，且飞书通知存在误用真实地址的风险
- **业务目标**：产出一个可复用、可配置、可全量扫描、可通知的 `/bug-sniff` 技能

## Phase 2: Data

- **规则来源**：`.claude/rules/07_ci_gates.md`
- **复用来源**：`githooks/pre-commit`
- **关键配置**：`config/settings.py`、`utils/feishu_api.py`
- **关键扫描目录**：`backend/`、`frontend/`、`.skills/`、`promptsRec/active/`、`promptsRec/archive/`
- **编号来源**：`promptsRec/.sequence`

## Phase 3: Architecture

- **组件划分**：`gates_scanner.py` 负责扫描，`feishu_reporter.py` 负责格式化与发送，`cli.py` 负责参数解析、执行编排和退出码
- **扫描策略**：以仓库根目录或显式传入路径为扫描范围，不依赖 git staged 状态
- **失败策略**：单个 gate 失败不应中断后续 gate；最终由汇总结果统一给出整体 PASS/FAIL
- **通知策略**：支持 `--dry-run` 或等效只渲染模式，避免本地开发默认外发消息

## Phase 4: Execution

按下述步骤实现，并在验证阶段覆盖 G1-G6 全部门禁。

# 执行步骤 / Execution Steps

## Step 1: 创建技能目录和元数据

创建 `.skills/bug-sniff/SKILL.md`，包含：
- frontmatter（name, executor, auto_invoke, depends_on, triggers, rules_ref, version）
- 技能说明
- 执行步骤
- 完成标准

## Step 2: 创建扫描脚本

创建 `scripts/bug_sniff/gates_scanner.py`，封装以下检查：

### G1 检查（复用 `githooks/pre-commit` 规则语义，改为全量扫描）
- G1-1: UTF-8 BOM 检测
- G1-2: 中文 SQL 字段检测（**修复**：使用 `grep -P '[\p{Han}]'` 或等效实现）
- G1-3: 占位符代码检测
- G1-4: 敏感信息检测（调用 `detect-secrets`）
- G1-5: 依赖版本锁定检测

### G2 检查
- G2-1: Python 静态分析（ruff）
- G2-2: ESLint（前端）
- G2-3: 外部表 DDL 操作检测

### G3 检查
- G3-1 ~ G3-4: pytest/vitest/playwright（依赖或目标目录未安装/不存在时 skip，并在报告中写明原因）

### G4 检查
- G4-1: 8D 文档结构检测（按 `promptsRec/active` 实际路径实现）
- G4-2: HOTFIX RFC 检测（按 `promptsRec/active` 实际路径实现）

### G5 检查
- G5-1 ~ G5-3: 归档命名/序号/前置条件检测

### G6 检查
- G6-1: 技能文件体积检查
- G6-2: Frontmatter 完整性检查
- G6-3: triggers 全局唯一性检查
- G6-4: depends_on 引用存在性检查

**注意**：G3 依赖 pytest/vitest/playwright，如未安装则该 gate 标记为 SKIP，不阻断其他检查。G6 需要对 `.skills/` 目录执行全量检查，而不是仅检查本次新建技能。

## Step 3: 创建飞书通知模块

在 `scripts/bug_sniff/feishu_reporter.py` 中：
- 定义报告格式化函数（markdown 格式）
- 通过 `config/settings.py` 读取现有 `FEISHU_*` 配置，禁止内嵌真实 URL
- 实现 Webhook 发送函数
- 支持分段发送（超长消息拆分成多条）
- 支持 dry-run 模式下只渲染不发送

## Step 4: 创建 CLI 入口

创建 `scripts/bug_sniff/cli.py`：
- 解析命令行参数
- 支持仓库路径参数与 `--dry-run`
- 依次执行 G1-G6 检查
- 汇总结果并在非 dry-run 模式下发送到飞书

## Step 5: 测试验证

1. 运行 `python scripts/bug_sniff/cli.py --dry-run`，确认 G1-G6 扫描无报错且不外发消息
2. 在已配置 `FEISHU_*` 的环境下运行通知模式，确认飞书收到报告卡片
3. 验证 FAIL 项包含文件路径和具体问题描述
4. 验证 `.skills/` 目录的 G6 检查已生效

# 完成标准 / Completion Criteria

- [ ] `/bug-sniff` 技能文件存在且 frontmatter 完整
- [ ] `scripts/bug_sniff/gates_scanner.py` 覆盖 G1-G6 所有 gate
- [ ] `scripts/bug_sniff/feishu_reporter.py` 正确发送飞书消息
- [ ] 飞书目标地址全部来自 `config/settings.py` 的现有配置或 CLI 注入，不存在硬编码真实 URL
- [ ] 运行 `python scripts/bug_sniff/cli.py --dry-run` 无报错
- [ ] 飞书 Webhook 收到包含 PASS/FAIL 状态的报告卡片
- [ ] G1-2 使用 `grep -P '[\p{Han}]'` 无 false positive

# 关键文件参考

| 文件 | 用途 |
|------|------|
| `githooks/pre-commit` | G1 检查逻辑来源 |
| `.claude/rules/07_ci_gates.md` | G1-G6 门禁规则定义 |
| `config/settings.py` | 飞书配置来源 |
| `utils/feishu_api.py` | 飞书 Webhook 发送参考 |
| `backend/database/schema/column_names.py` | 字段名常量（用于 G2-3 检测） |
