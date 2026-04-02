# 事件捕获 / INCIDENT CAPTURE

---

## 目的 / Purpose

捕获运行时错误、日志或意外系统行为，并将其转换为结构化的事件记录。 / Capture runtime errors, logs, or unexpected system behaviors and convert them into a structured incident record.

此技能准备事件数据，以便 `bug-triage` 可以分析并生成 bug 修复提示词。 / This skill prepares incident data so that `bug-triage` can analyze it and generate a bug-fix prompt.

此技能不直接修复问题。 / This skill does NOT fix the issue directly.

---

## 输入来源 / Input Sources

事件数据可能来自: / Incident data may come from:

- 运行时日志 / runtime logs
- 堆栈跟踪 / stack traces
- 后端异常 / backend exceptions
- 前端控制台错误 / frontend console errors
- 数据库错误 / database errors
- 用户 bug 报告 / user bug reports
- 截图或描述 / screenshots or descriptions
- incidents/gui_events/GUI_EVENT_*.json  # GUI Launcher 生成的事件文件

---

## 事件识别 / Incident Identification

尽可能提取以下信息: / Extract the following information if possible:

- 事件摘要 / Incident Summary
- 受影响模块 / Affected Module
- 错误消息 / Error Message
- 堆栈跟踪 / Stack Trace
- 观察到的行为 / Observed Behavior
- 预期行为 / Expected Behavior
- 发生时间 / Time of Occurrence

---

## 受影响区域分类 / Affected Area Classification

确定涉及的系统区域。 / Determine the system area involved.

可能值: / Possible values:

- 架构 / Architecture
- 后端 / Backend
- 数据库 / Database
- API
- 前端 / Frontend
- 集成 / Integration
- 通知系统 / Notification System
- 运输工作流 / Transport Workflow

如不确定，标记为: / If uncertain, mark as:

未知 / Unknown

---

## 严重性分类 / Severity Classification

使用以下级别分类严重性: / Classify severity using the following levels:

- 严重 / Critical
- 高 / High
- 中 / Medium
- 低 / Low

指南: / Guidelines:

严重 / Critical
- 系统崩溃 / system crash
- 数据库损坏风险 / database corruption risk
- 工作流完全受阻 / workflow completely blocked

高 / High
- 核心功能不可用 / core function unavailable
- API 失败 / API failure

中 / Medium
- 部分工作流问题 / partial workflow issue

低 / Low
- UI 问题或非关键行为 / UI issue or non-critical behavior

---

## 输出文件 / Output Files

生成以下文件: / Generate the following file:

`incidents/INCIDENT_[时间戳]_[简短名称].md`

示例: / Example:

`INCIDENT_20260312_submit_error.md`

---

## 事件文件结构 / Incident File Structure

生成的事件文件必须包含: / The generated incident file must contain:

- 事件摘要 / Incident Summary
- 受影响区域 / Affected Area
- 严重性 / Severity
- 错误消息 / Error Message
- 堆栈跟踪 / Stack Trace
- 观察到的行为 / Observed Behavior
- 预期行为 / Expected Behavior
- 可能根本原因 / Possible Root Cause

---

## 下一步建议 / Next Step Recommendation

生成事件文件后，建议运行: / After generating the incident file, recommend running:

`bug-triage`

这将把事件转换为 bug 修复提示词。 / This will convert the incident into a bug-fix prompt.

---

## 约束 / Constraints

此技能严禁: / This skill must NOT:

- 修改后端代码 / modify backend code
- 修改前端代码 / modify frontend code
- 修改数据库 Schema / modify database schema
- 重命名提示词文件 / rename prompt files
- 执行 bug 修复 / execute bug fixes

它仅记录事件并为分类准备数据。 / It only records incidents and prepares data for triage.

---

## 完成标准 / Completion Criteria

当以下条件满足时，技能完成: / The skill is complete when:

1. `incidents/` 下存在事件文件 / An incident file exists in `incidents/`
2. 事件信息已结构化 / The incident information is structured
3. 问题已准备好供 `bug-triage` 处理 / The issue is ready for `bug-triage`
