# 事件监控 / INCIDENT MONITOR

---

## 目的 / Purpose

监控事件来源并识别应捕获为结构化事件的新运行时问题。 / Monitor incident sources and identify new runtime problems that should be captured as structured incidents.

此技能不直接修复问题。 / This skill does NOT fix issues directly.
此技能不直接生成 bug 修复提示词。 / This skill does NOT generate bug-fix prompts directly.

其职责是: / Its responsibility is:

1. 检测潜在事件 / detect potential incidents
2. 总结发现的内容 / summarize what was found
3. 建议运行 `incident-capture` / recommend running `incident-capture`

---

## 支持的来源 / Supported Sources

此技能可以检查以下来源（如果存在）: / This skill may inspect the following sources if they exist:

- 后端日志 / backend logs
- 前端控制台错误日志 / frontend console error logs
- 发布预检报告 / release precheck reports
- 运行时异常报告 / runtime exception reports
- 用户提供的错误文本 / user-provided error text
- 事件文件夹 / incident folders
- 截图或复制的堆栈跟踪 / screenshots or copied stack traces

典型位置可能包括: / Typical locations may include:

```
logs/
docs/RELEASE_PRECHECK_REPORT.md
incidents/
incidents/gui_events/   # GUI Launcher 生成的事件文件 (GUI_EVENT_*.json)
```

当发现新的 `GUI_EVENT_*.json` 文件时：
1. 读取事件内容
2. 在 `INCIDENT_MONITOR_REPORT.md` 中建议运行 `incident-capture`
3. 将事件文件路径作为 incident-capture 的输入

如果来源不存在，则跳过。 / If a source does not exist, skip it.

---

## 监控目标 / Monitoring Goal

识别是否存在应成为事件记录的新未解决问题。 / Identify whether there is a new unresolved issue that should become an incident record.

候选事件通常包括以下一项或多项: / A candidate incident usually includes one or more of the following:

- 错误消息 / error message
- 异常名称 / exception name
- 堆栈跟踪 / stack trace
- 失败的 API 调用 / failed API call
- 数据库错误 / database error
- 重复的警告表示工作流失败 / repeated warning indicating workflow failure
- 发布预检项标记为严重或高 / release precheck item marked as Critical or High
- 用户报告描述被阻止的工作流 / user report describing a blocked workflow

---

## 检测规则 / Detection Rules

如果满足以下任何条件，则将问题视为候选事件: / Treat an issue as a candidate incident if any of the following is true:

1. 存在明确的异常或回溯 / a clear exception or traceback is present
2. 数据库操作失败 / a database operation failed
3. 核心工作流操作失败 / a core workflow action failed
4. API 请求重复失败 / an API request failed repeatedly
5. 发布预检包含未解决的严重或高问题 / release precheck contains unresolved Critical or High issues
6. 用户报告的问题阻止主要工作流 / a user-reported problem blocks the main workflow

如果多条记录描述相同的底层问题，将它们归为一个候选事件。 / If multiple records describe the same underlying issue, group them as one incident candidate.

---

## 去重规则 / De-duplication Rules

在推荐新事件之前，检查以下位置是否已存在类似事件: / Before recommending a new incident, check whether a similar incident already exists in:

`incidents/`

如果类似事件已存在且仍未解决，不要创建重复推荐。 / If a similar incident already exists and is still unresolved, do NOT create a duplicate recommendation.

使用以下线索判断相似性: / Use the following clues for similarity:

- 相同的错误消息 / same error message
- 相同的模块 / same module
- 相同的失败操作 / same failing action
- 相同的堆栈跟踪模式 / same stack trace pattern
- 相同的数据库列/表错误 / same database column / table error

---

## 输出 / Output

生成监控摘要报告: / Generate a monitoring summary report:

`docs/INCIDENT_MONITOR_REPORT.md`

报告必须包含: / The report must include:

1. 扫描范围 / scan scope
2. 检查的来源 / sources checked
3. 检测到的候选事件 / detected incident candidates
4. 跳过的重复项 / duplicates skipped
5. 建议 / recommendation

---

## 报告结构 / Report Structure

报告应包含以下部分: / The report should contain these sections:

```
# 事件监控报告 / Incident Monitor Report

## 扫描摘要 / Scan Summary
- 时间: / Time:
- 检查的来源: / Sources Checked:
- 新候选事件: / New Incident Candidates:
- 现有类似事件: / Existing Similar Incidents:
- 建议: / Recommendation:

## 候选事件 / Candidate Incidents
为每个候选包含: / For each candidate include:
- 摘要 / Summary
- 受影响区域 / Affected Area
- 严重性建议 / Severity Suggestion
- 证据 / Evidence
- 建议的下一步操作 / Recommended Next Action

## 重复或现有事件 / Duplicate or Existing Incidents
- 现有事件文件 / Existing Incident File
- 被视为重复的原因 / Reason Considered Duplicate

## 最终建议 / Final Recommendation
以下之一: / One of:
- 运行 incident-capture / Run incident-capture
- 不需要新的事件操作 / No new incident action required
```

---

## 严重性建议规则 / Severity Suggestion Rules

使用以下级别建议严重性: / Suggest severity using these levels:

- 严重 / Critical
- 高 / High
- 中 / Medium
- 低 / Low

指南: / Guidance:

严重 / Critical
- 系统崩溃 / system crash
- 数据库损坏风险 / database corruption risk
- 出库/入库工作流完全受阻 / outbound/inbound workflow completely blocked

高 / High
- 主要功能损坏 / major feature broken
- 提交/确认/通知无法完成 / submit / confirm / notify cannot complete

中 / Medium
- 部分失败 / partial failure
- 需要重试 / retry needed
- 非核心工作流问题 / non-core workflow issue

低 / Low
- 外观问题 / cosmetic issue
- 孤立警告 / isolated warning
- 非阻塞性问题 / non-blocking problem

---

## 建议规则 / Recommendation Rules

如果至少存在一个新的候选事件: / If at least one new candidate incident exists:

建议: / Recommend:
运行 incident-capture / Run incident-capture

如果不存在新的候选事件: / If no new candidate exists:

建议: / Recommend:
不需要新的事件操作 / No new incident action required

如果只发现重复项: / If only duplicates were found:

建议: / Recommend:
在创建新事件之前查看现有事件文件 / Review existing incident files before creating a new one

---

## 约束 / Constraints

此技能严禁: / This skill must NOT:

- 修改后端代码 / modify backend code
- 修改前端代码 / modify frontend code
- 修改数据库 Schema / modify database schema
- 创建 bug 修复提示词 / create bug-fix prompts
- 重命名提示词文件 / rename prompt files
- 执行 RUNPROMPT 任务 / execute RUNPROMPT tasks
- 直接创建事件文件 / create incident files directly

此技能仅监控并建议下一步操作。 / This skill only monitors and recommends the next action.

---

## 完成标准 / Completion Criteria

当以下条件满足时，技能完成: / The skill is complete when:

1. `docs/INCIDENT_MONITOR_REPORT.md` 存在 / docs/INCIDENT_MONITOR_REPORT.md exists
2. 如果发现新候选事件，必须清楚列出 / new candidate incidents are clearly listed if found
3. 如果发现重复事件，必须清楚识别 / duplicate incidents are identified if found
4. 最终建议必须清楚陈述 / the final recommendation is clearly stated
