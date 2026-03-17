# 事件响应流程 / INCIDENT_RESPONSE_FLOW

---

## 目的 / Purpose

本文档描述运行时事件如何被检测、记录、分析并转换为修复任务。 / This document describes how runtime incidents are detected, recorded, analyzed, and converted into repair tasks.

目标是确保系统可以在部署后持续演进。 / The goal is to ensure the system can continuously evolve after deployment.

---

# 事件生命周期 / Incident Lifecycle

运行时问题遵循结构化生命周期。 / Runtime issues follow a structured lifecycle.

运行时错误 / Runtime error
→ 事件监控 / incident-monitor
→ 事件捕获 / incident-capture
→ Bug 分类 / bug-triage
→ Bug 修复提示词 / bug fix prompt
→ RUNPROMPT 执行 / RUNPROMPT execution
→ 发布预检 / release-precheck

这形成了一个持续的 AI 辅助修复循环。 / This forms a continuous AI-assisted repair loop.

---

# 步骤 1: 事件监控 / Step 1: Incident Monitor

技能: / Skill:

`skills/incident-monitor`

目的: / Purpose:

扫描系统信号并确定是否应该记录新事件。 / Scan system signals and determine whether a new incident should be recorded.

可能来源包括: / Possible sources include:

```
logs - 日志
stack traces - 堆栈跟踪
user bug reports - 用户 bug 报告
release precheck failures - 发布预检失败
backend exceptions - 后端异常
frontend console errors - 前端控制台错误
```

该技能生成监控报告: / The skill produces a monitoring report:

`docs/INCIDENT_MONITOR_REPORT.md`

如果检测到新问题，建议运行 incident-capture。 / If a new issue is detected, it recommends running incident-capture.

---

# 步骤 2: 事件捕获 / Step 2: Incident Capture

技能: / Skill:

`skills/incident-capture`

目的: / Purpose:

将原始运行时问题转换为结构化事件记录。 / Convert raw runtime problems into a structured incident record.

输出位置: / Output location:

`incidents/`

示例文件: / Example file:

`INCIDENT_20260312_submit_error.md`

每个事件记录包括: / Each incident record includes:

- 事件摘要 / incident summary
- 受影响区域 / affected area
- 严重性 / severity
- 错误消息 / error message
- 堆栈跟踪 / stack trace
- 观察到的行为 / observed behavior
- 预期行为 / expected behavior
- 可能根本原因 / possible root cause

此文件成为事件的正式记录。 / This file becomes the formal record of the incident.

---

# 步骤 3: Bug 分类 / Step 3: Bug Triage

技能: / Skill:

`skills/bug-triage`

目的: / Purpose:

分析事件并将其转换为 bug 修复提示词。 / Analyze the incident and convert it into a bug-fix prompt.

该技能确定: / The skill determines:

- 严重性 / severity
- 受影响的子系统 / affected subsystem
- 负责的执行者 / responsible executor

新提示词创建在: / A new prompt is created inside:

`promptsRec/`

示例: / Example:

`101_bug_missing_column.md`

---

# 步骤 4: Bug 修复任务 / Step 4: Bug Fix Task

生成的提示词将包含以下元数据: / The generated prompt will contain metadata such as:

- 主要执行者 / Primary Executor
- 任务类型 / Task Type
- 目标 / Goal

示例执行者路由: / Example executor routing:

| 问题类型 / Issue Type | 执行者 / Route to |
|---------------------|-----------------|
| 架构问题 / Architecture issues | Claude Code |
| 后端或数据库问题 / Backend or database issues | Codex |
| 前端设计问题 / Frontend design issues | Gemini |
| 前端实现问题 / Frontend implementation issues | Codex |

然后使用以下命令执行 bug 修复任务: / The bug fix task is then executed using:

`RUNPROMPT`

---

# 步骤 5: 验证 / Step 5: Verification

实现 bug 修复后，系统应运行: / After the bug fix is implemented, the system should run:

`release-precheck`

这确保修复没有引入新的不一致。 / This ensures the fix did not introduce new inconsistencies.

---

# 去重规则 / De-duplication Rule

在创建新事件之前，系统应检查以下位置中的现有文件: / Before creating a new incident, the system should check existing files in:

`incidents/`

如果相同问题已存在，避免创建重复事件。 / If the same issue already exists, avoid creating duplicate incidents.

相反，更新现有记录。 / Instead, update the existing record.

---

# 严重性级别 / Severity Levels

事件使用四个级别分类。 / Incidents are classified using four levels.

**严重 / Critical**
系统崩溃或工作流完全受阻。 / System crash or workflow completely blocked.

**高 / High**
核心功能损坏。 / Core function broken.

**中 / Medium**
部分失败或功能降级。 / Partial failure or degraded functionality.

**低 / Low**
小型 UI 或非阻塞性问题。 / Minor UI or non-blocking issue.

---

# 结果 / Result

此事件响应流程使系统能够: / This incident response flow enables the system to:

- 检测运行时问题 / detect runtime issues
- 以结构化形式记录事件 / record incidents in structured form
- 将事件转换为修复任务 / convert incidents into repair tasks
- 在发布前验证修复 / verify fixes before release

该流程确保系统在部署后持续改进。 / The process ensures continuous improvement of the system after deployment.
