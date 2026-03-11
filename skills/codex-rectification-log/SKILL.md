---
name: codex-rectification-log
description: 每次 Codex 发现缺陷、实现修复并在此仓库中完成相关纠正或审查驱动的更改时，记录纠正日志。当 Codex 完成更改代码或文档以纠正错误、bug、回归、验证问题或审查发现时使用，必须在关闭任务前将记录保存到 logs/codex_rectification。/ Record a rectification log whenever Codex identifies a defect, implements the fix, and completes the related correction or review-driven change in this repository. Use when Codex has finished changing code or docs to correct an error, bug, regression, validation issue, or review finding, and must save a record under logs/codex_rectification before closing the task.
---

# Codex 纠正日志 / Codex Rectification Log

为每个完成的纠正写入一条纠正记录。 / Write one rectification record for every completed correction.

仅在所有请求的编辑完成后创建日志。 / Create the log only after all requested edits are finished.

如果没有文件被更改，则不要创建纠正记录。 / If no file was changed, do not create a rectification record.

如果任务仅是审查且未实施纠正，则不要创建纠正记录。 / If the task is review-only and no correction was implemented, do not create a rectification record.

## 日志位置 / Log location

将记录保存到 `logs/codex_rectification/`。 / Save records under `logs/codex_rectification/`.

如果目录不存在，则创建。 / Create the directory if it does not exist.

## 文件名规则 / Filename rule

使用 `rectification_[YYYYMMDD_HHMMSS]_[简短摘要].md`。 / Use `rectification_[YYYYMMDD_HHMMSS]_[short-summary].md`.

将 `short-summary` 保持为小写连字符格式并简洁。 / Keep `short-summary` in lowercase hyphen-case and concise.

示例: / Example:

`rectification_20260311_153045_fix-health-status-code.md`

## 必需的工作流程 / Required workflow

1. 检查为纠正而更改的文件。 / Inspect the files that were changed for the correction.
2. 用具体术语总结原始缺陷。 / Summarize the original defect in concrete terms.
3. 总结实施的纠正。 / Summarize the implemented correction.
4. 记录实际执行的验证。如果未运行验证，明确说明。 / Record verification actually performed. If verification was not run, state that explicitly.
5. 在发送最终用户响应之前，将日志保存到 `logs/codex_rectification/`。 / Save the log under `logs/codex_rectification/` before sending the final user response.

## 必需内容 / Required content

使用以下结构: / Use this structure:

```md
# Codex 纠正记录 / Codex Rectification Record

## 基本信息 / Basic Information
- 时间: / Time:
- 执行者: Codex / Executor: Codex
- 摘要: / Summary:

## 触发 / Trigger
- 来源: [用户报告 | 代码审查 | 自检 | 测试失败 | 其他] / Source: [user report | code review | self-check | test failure | other]
- 上下文: / Context:

## 缺陷 / Defect
- 描述: / Description:
- 影响: / Impact:

## 纠正 / Correction
- 更新的文件: / Files Updated:
- 更改摘要: / Change Summary:

## 验证 / Verification
- 执行: / Performed:
- 结果: / Result:

## 备注 / Notes
-
```

## 内容规则 / Content rules

仅写入事实性条目。 / Write factual entries.

使用仓库相对路径引用更改的文件。 / Reference changed files with repository-relative paths.

保持日志简洁。优先使用短项目符号而不是长段落。 / Keep the log concise. Prefer short bullets over long prose.

如果在一个任务中修复了多个缺陷，当它们属于同一纠正集时，将它们分组到一条记录中。仅当修复明显无关时才创建单独的记录。 / If multiple defects are fixed in one task, group them in a single record when they belong to the same correction set. Create separate records only when the fixes are clearly unrelated.

当纠正直接来自审查时，在 `来源` 中提及并在 `上下文` 中总结发现。 / When a correction comes directly from a review, mention that in `Source` and summarize the finding in `Context`.

不要声称未实际执行的验证。 / Do not claim verification that was not actually performed.
