name: repo-context-firewall
executor: Claude Code
description: 检测超大文件和上下文繁重的仓库区域，然后推荐或应用上下文优化规则，以减少 Trae token 使用并提高 AI 开发速度。/ Detect oversized files and context-heavy repository areas, then recommend or apply context optimization rules to reduce Trae token usage and improve AI development speed.

---

# 仓库上下文防火墙技能 / Repo Context Firewall Skill

## 目的 / Purpose

此技能保护仓库免受上下文爆炸。/ This skill protects the repository from context explosion.

其主要目标是通过防止超大或低价值文件被重复加载到 AI 上下文中来减少 Trae 内置模型的 token 消耗。/ Its primary goal is to reduce token consumption for Trae built-in models by preventing oversized or low-value files from being repeatedly loaded into AI context.

其次要目标是通过减少不必要的仓库扫描来提高 Claude Code 和 Codex 的开发速度。/ Its secondary goal is to improve Claude Code and Codex development speed by reducing unnecessary repository scanning.

此技能不直接实现业务功能。/ This skill does NOT directly implement business features.

它专注于仓库上下文效率。/ It focuses on repository context efficiency.

## 核心价值 / CORE VALUE

对于 Trae 内置模型：/ For Trae built-in models:
- 减少 token 成本 / reduce token cost
- 减少上下文污染 / reduce context pollution
- 减少无关文件的加载 / reduce loading of irrelevant files

对于 Claude Code 和 Codex：/ For Claude Code and Codex:
- 提高仓库扫描速度 / improve repo scan speed
- 减少大文件分析开销 / reduce large-file analysis overhead
- 使 bug 修复和功能实现更加专注 / make bug fixing and feature implementation more focused

## 何时使用 / WHEN TO USE

在以下情况下使用此技能：/ Use this skill when:

- 仓库变得很大 / the repository becomes large
- AI 响应变慢 / AI responses become slower
- Trae token 使用变得昂贵 / Trae token usage becomes expensive
- 审查报告积累 / review reports accumulate
- 日志和构建产物增加 / logs and build artifacts increase
- 后端核心文件变得太大 / backend core files become too large
- 文档量显著增长 / documentation volume grows significantly

此技能应作为仓库维护定期使用。/ This skill should be used periodically as repository maintenance.

## 步骤 1 — 扫描上下文热点 / STEP 1 — SCAN FOR CONTEXT HOTSPOTS

检查仓库并识别可能浪费 AI 上下文的文件或目录。/ Inspect the repository and identify files or directories that are likely to waste AI context.

典型热点包括：/ Typical hotspots include:

- 大于 200 KB 的文件 / files larger than 200 KB
- 超过 500 行的源文件 / source files longer than 500 lines
- 生成的报告 / generated reports
- 日志 / logs
- 构建产物 / build artifacts
- 重复的文档 / duplicated documents
- 归档的提示词执行记录 / archived prompt execution records
- 临时文件 / temporary files

## 步骤 2 — 分类热点 / STEP 2 — CLASSIFY HOTSPOTS

将每个热点分类到以下组之一：/ Classify each hotspot into one of the following groups:

### 组 A — 可安全忽略 / GROUP A — Safe to Ignore

示例：/ Examples:
- 构建输出 / build outputs
- 依赖文件夹 / dependency folders
- 日志 / logs
- 生成的报告 / generated reports
- 临时文件 / temp files

### 组 B — 保留但避免频繁加载 / GROUP B — Keep but Avoid Frequent Loading

示例：/ Examples:
- 大型稳定文档 / large stable documentation
- 归档的提示词历史 / archived prompt history
- 已完成的运行摘要 / completed run summaries
- 旧的审查文档 / old review documents

### 组 C — 必须保持可见但应拆分 / GROUP C — Must Stay Visible but Should Be Split

示例：/ Examples:
- 超大的后端源文件 / oversized backend source files
- 超大的前端源文件 / oversized frontend source files
- 超大的路由文件 / oversized route files
- 超大的查询模块 / oversized query modules

## 步骤 3 — 更新 .trae/.ignore / STEP 3 — UPDATE .trae/.ignore

对于组 A 和适当的组 B 项目：/ For Group A and appropriate Group B items:

- 创建或更新 .trae/.ignore / create or update .trae/.ignore
- 添加忽略规则 / add ignore rules
- 避免重复规则 / avoid duplicate rules
- 保留重要的源目录 / preserve important source directories

永远不要忽略：/ Never ignore:
- backend/
- frontend/src/
- promptsRec/active/
- promptsRec/archive/
- .skills/
- 重要的架构入口文档 / essential architecture entry documents

## 步骤 4 — 生成拆分建议 / STEP 4 — GENERATE SPLIT RECOMMENDATIONS

对于组 C 文件：/ For Group C files:

不要在此技能中自动重构它们 / do NOT automatically refactor them in this skill

而是生成包含以下内容的结构化建议列表：/ Instead generate a structured recommendation list including:

- 文件路径 / file path
- 大致大小 / approximate size
- 上下文繁重的原因 / reason it is context-heavy
- 建议的拆分策略 / suggested split strategy

示例：/ Examples:

```
database.py
建议拆分:
- database/core.py
- database/order_queries.py
- database/tool_queries.py
- database/rbac_queries.py

web_server.py
建议拆分:
- routes/auth_routes.py
- routes/order_routes.py
- routes/tool_routes.py
- routes/dashboard_routes.py
```

## 步骤 5 — 保留主动开发上下文 / STEP 5 — PRESERVE ACTIVE DEVELOPMENT CONTEXT

此技能必须确保以下内容对 AI 开发保持可见：/ The skill must ensure the following remain visible for AI development:

- 主动的后端源文件 / active backend source files
- 前端 src 文件 / frontend src files
- promptsRec/active/ 下的当前提示词 / current prompts under promptsRec/active/
- 架构索引 / architecture index
- 当前 API 合约快照 / current API contract snapshot
- 当前编辑的技能定义 / currently edited skill definitions

目的是优化，不是盲目。/ The purpose is optimization, not blindness.

## 步骤 6 — 输出防火墙报告 / STEP 6 — OUTPUT A FIREWALL REPORT

创建或更新报告：/ Create or update a report:

`docs/REPO_CONTEXT_FIREWALL.md`

报告必须包括：/ The report must include:

- 最大文件 / largest files
- 最耗费 token 的目录 / most token-expensive directories
- 忽略的目录 / ignored directories
- 建议拆分的文件 / files recommended for splitting
- 安全的优化操作 / safe optimization actions
- Trae token 浪费的高风险区域 / high-risk areas for Trae token waste

## 步骤 7 — 可选的轻量级强制 / STEP 7 — OPTIONAL LIGHTWEIGHT ENFORCEMENT

如果安全且明显，此技能可以更新：/ If safe and obvious, the skill may update:

`.trae/.ignore`

但它必须不能：/ But it must NOT:
- 删除文件 / delete files
- 移动文件 / move files
- 自动重构源代码 / refactor source code automatically
- 隐藏重要的架构文档 / hide essential architecture documents

## 预期结果 / EXPECTED RESULT

执行后：/ After execution:

- Trae 内置模型的 token 使用减少 / Trae built-in model token usage is reduced
- 不必要的仓库区域被忽略 / unnecessary repo areas are ignored
- 超大文件被识别 / oversized files are identified
- 拆分候选被记录 / split candidates are documented
- Claude Code 和 Codex 可以更快地导航仓库 / Claude Code and Codex can navigate the repo faster
- 仓库维护变得更高效 / repository maintenance becomes more efficient
- docs/REPO_CONTEXT_FIREWALL.md 存在并包含最新的热点、分类、忽略规则、拆分建议和操作 / docs/REPO_CONTEXT_FIREWALL.md exists and is up to date with the latest hotspots, classifications, ignore rules, split recommendations, and safe actions
- .trae/.ignore 包含最新的安全忽略和拆分建议 / .trae/.ignore is up to date with the latest safe-to-ignore and split recommendations
- 主动开发上下文对 AI 开发保持可见 / active development context remains visible for AI development
