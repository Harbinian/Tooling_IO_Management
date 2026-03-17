name: token-context-optimizer
executor: Claude Code
description: 维护 .trae/.ignore 以通过从 AI 上下文扫描中排除大型或无关文件来减少 token 使用。/ Maintain .trae/.ignore to reduce token usage by excluding large or irrelevant files from AI context scanning.

---

# Token 上下文优化器技能 / Token Context Optimizer Skill

## 目的 / PURPOSE

此技能减少 AI 辅助开发期间的 token 消耗。/ This skill reduces token consumption during AI-assisted development.

它维护文件：/ It maintains the file:

`.trae/.ignore`

此文件告诉 AI 环境在加载仓库上下文时哪些目录和文件不应该被扫描。/ This file tells the AI environment which directories and files should NOT be scanned when loading repository context.

目标是让 AI 上下文专注于：/ The goal is to keep AI context focused on:

后端源代码 / backend source code
前端源代码 / frontend source code
主动提示词 / active prompts
基本架构文档 / essential architecture documents

并忽略其他一切。/ and ignore everything else.

## 何时使用 / WHEN TO USE

在以下情况下使用此技能：/ Use this skill when:

仓库变大 / repository grows large
AI 响应变慢 / AI responses become slower
审查报告积累 / review reports accumulate
出现大型日志 / large logs appear
构建产物增加 / build artifacts increase
token 使用激增 / token usage spikes

此技能应偶尔执行以保持仓库对 AI 友好。/ This skill should be executed occasionally to keep the repository AI-friendly.

## 步骤 1 — 确保 .trae 目录存在 / STEP 1 — ENSURE .trae DIRECTORY

检查仓库是否包含：/ Check whether the repository contains:

`.trae/`

如果不存在：/ If it does not exist:

创建目录 ".trae" / create directory ".trae"

## 步骤 2 — 创建或更新忽略文件 / STEP 2 — CREATE OR UPDATE IGNORE FILE

确保文件存在：/ Ensure the file exists:

`.trae/.ignore`

如果已存在：/ If it already exists:

追加缺失的规则 / append missing rules
不重复现有条目 / do not duplicate existing entries

## 步骤 3 — 忽略依赖目录 / STEP 3 — IGNORE DEPENDENCY DIRECTORIES

为依赖文件夹添加规则：/ Add rules for dependency folders:

```
node_modules/
venv/
.venv/
__pycache__/
```

这些文件夹永远不应该被 AI 扫描。/ These folders should never be scanned by AI.

## 步骤 4 — 忽略构建产物 / STEP 4 — IGNORE BUILD ARTIFACTS

为编译输出添加规则：/ Add rules for compiled outputs:

```
dist/
build/
frontend/dist/
frontend/build/
```

这些目录包含生成的文件。/ These directories contain generated files.

## 步骤 5 — 忽略日志和临时文件 / STEP 5 — IGNORE LOG AND TEMP FILES

为临时文件添加规则：/ Add rules for temporary files:

```
*.log
*.tmp
*.map
*.cache
```

这些文件对 AI 推理没有帮助。/ These files do not help AI reasoning.

## 步骤 6 — 忽略生成的报告 / STEP 6 — IGNORE GENERATED REPORTS

生成的报告通常消耗大量 token。/ Generated reports often consume large tokens.

忽略以下目录：/ Ignore directories such as:

```
review-reports/
run_records/
logs/
```

这些文件可供手动阅读，但不应自动扫描。/ These files remain available for manual reading but should not be scanned automatically.

## 步骤 7 — 保留重要目录 / STEP 7 — PRESERVE IMPORTANT DIRECTORIES

永远不要忽略以下目录：/ Never ignore these directories:

```
backend/
frontend/src/
promptsRec/active/
promptsRec/archive/
docs/
.skills/
```

这些包含主动开发逻辑。/ These contain active development logic.

## 步骤 8 — 验证配置 / STEP 8 — VALIDATE CONFIGURATION

更新 .trae/.ignore 后验证：/ After updating .trae/.ignore verify:

后端代码保持可见 / backend code remains visible
前端 src 保持可见 / frontend src remains visible
promptsRec/active/ 保持可见 / promptsRec/active/ remains visible
promptsRec/archive/ 保持可见 / promptsRec/archive/ remains visible
技能保持可见 / skills remain visible

确认忽略的目录不再被扫描。/ Confirm ignored directories are no longer scanned.

## 预期结果 / EXPECTED RESULT

执行后：/ After execution:

`.trae/.ignore` 存在 / .trae/.ignore exists
大型目录被忽略 / large directories are ignored
token 消耗减少 / token consumption decreases
AI 上下文保持在主动代码和基本文档上 / AI context stays focused on active code and essential docs
