# 提示词任务约定 / Prompt Task Convention

---

## 目的 / Purpose

定义提示词文件的编写、执行和归档方式。 / Define how prompt files are written, executed, and archived.

## 提示词目录 / Prompt directory

所有可执行的提示词任务位于: / All executable prompt tasks live in:

`promptsRec/`

## 待处理任务格式 / Pending task format

示例: / Examples:

- `001.md`
- `002_generate_docs.md`
- `010_backend_api.md`

## 已完成任务格式 / Completed task format

示例: / Examples:

- `✅_00001_001_生成PRD架构.md`
- `✅_00002_002_generate_docs_补充接口文档.md`

## 提示词文件编写规则 / Writing rules for prompt files

每个提示词应包含: / Each prompt should include:

1. 明确的目标 / clear objective
2. 预期输出 / expected outputs
3. 约束条件 / constraints
4. 目标文件（如果已知）/ target files if known
5. 完成标准 / completion criteria

## 提示词示例 / Example prompt

```md
生成以下文件: / Generate the following files:
- docs/PRD.md
- docs/ARCHITECTURE.md

需求: / Requirements:
- 定义出库工作流 / define outbound workflow
- 定义入库工作流 / define inbound workflow
- 定义状态机 / define state machines
- 使用项目规则作为约束 / use project rules as constraints
