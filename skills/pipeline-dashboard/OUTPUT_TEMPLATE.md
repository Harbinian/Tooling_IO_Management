# 流水线状态 / Pipeline Status

## 摘要 / Summary

已完成: <number> / Completed: <number>
运行中: <number> / Running: <number>
待处理: <number> / Pending: <number>

---

## 进度 / Progress

<进度条> <百分比>% / <progress_bar> <percent>%

示例: / Example:

██████████░░ 60%

进度计算: / Progress calculation:

进度 = 已完成 / (已完成 + 待处理) / progress = completed / (completed + pending)

进度条长度: 10 单位 / Bar length: 10 units

---

## 已完成的任务 / Completed Tasks

- <归档提示词文件> / <archived_prompt_file>
- <归档提示词文件> / <archived_prompt_file>

示例: / Example:

- ✅_00001_001_generate_prd.md
- ✅_00002_002_architecture_design.md

---

## 运行中的任务 / Running Tasks

- <锁文件> / <lock_file>

示例: / Example:

- 003_backend_implementation.lock

如果没有: / If none:

无 / None

---

## 待处理任务 / Pending Tasks

- <提示词文件> [依赖状态] / <prompt_file> [dependency status]
- <提示词文件> [依赖状态] / <prompt_file> [dependency status]

依赖状态 / Dependency Status:
- ✅ = 依赖满足 / Dependencies satisfied
- ⏳ = 等待依赖 / Waiting for dependency

示例: / Example:

- 103_bug_fix.md ✅
- 025_frontend_feature.md ⏳ (等待 keeper_confirmation 后端完成)
- 026_another_feature.md ✅

---

## 下一个推荐任务 / Next Recommended Task

文件: <提示词文件> / File: <prompt_file>

执行者: <Claude Code | Codex | Gemini> / Executor: <Claude Code | Codex | Gemini>

依赖状态: ✅ 或 ⏳ 等待 <依赖> / Dependency Status: ✅ or ⏳ Waiting for <dependency>

命令: / Command:

RUNPROMPT promptsRec/<提示词文件> / RUNPROMPT promptsRec/<prompt_file>

---

## 等待依赖的任务 / Tasks Waiting for Dependencies

- <任务>: 等待 <依赖任务> 完成 / <task>: waiting for <dependency> to complete

如果没有: / If none:

无 / None

---

## 备注 / Notes

- 一次只应运行一个任务。 / Only one task should run at a time.
- 如果存在 `.lock` 文件，请等待其清除。 / If a `.lock` file exists, wait until it is cleared.
- 此技能不执行任务。 / This skill does NOT execute tasks.
