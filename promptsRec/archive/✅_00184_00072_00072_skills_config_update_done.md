Primary Executor: Claude Code
Task Type: Feature Development
Priority: P2
Stage: 00072
Goal: 实现 GUI Launcher 与 Skills 的事件联动 - Skills 配置更新
Dependencies: 00071
Execution: RUNPROMPT

---

## Context / 上下文

接续任务 00071，在 `dev_server_launcher.py` 实现事件写入后，需要更新 Skills 配置使其能扫描和捕获 GUI 事件。

---

## Required References / 必需参考

- `.skills/incident-monitor/SKILL.md` - 事件监控技能
- `.skills/incident-capture/SKILL.md` - 事件捕获技能
- `.claude/rules/01_workflow.md` - ADP 开发协议

---

## Core Task / 核心任务

### 1. 更新 incident-monitor 技能

在 `.skills/incident-monitor/SKILL.md` 的"监控来源"部分增加：

```
incidents/gui_events/   # GUI Launcher 生成的事件文件 (GUI_EVENT_*.json)
```

当发现新的 `GUI_EVENT_*.json` 文件时：
1. 读取事件内容
2. 在 `INCIDENT_MONITOR_REPORT.md` 中建议运行 `incident-capture`
3. 将事件文件路径作为 incident-capture 的输入

### 2. 更新 incident-capture 技能

在 `.skills/incident-capture/SKILL.md` 的"输入来源"部分增加：

```
incidents/gui_events/GUI_EVENT_*.json  # GUI Launcher 生成的事件文件
```

GUI 事件作为有效输入源，应能：
1. 被识别为有效事件
2. 生成 `incidents/INCIDENT_*.md` 事件记录
3. 触发 self-healing-dev-loop 流程

### 3. 创建目录和 .gitignore

1. 创建目录 `incidents/gui_events/`
2. 在 `.gitignore` 中添加：
   ```
   incidents/gui_events/*.json
   ```

---

## Required Work / 必需工作

1. 修改 `.skills/incident-monitor/SKILL.md`：
   - 在"监控来源"部分增加 `incidents/gui_events/` 说明
   - 更新检测规则，支持扫描 `GUI_EVENT_*.json` 文件
   - 在输出中包含 GUI 事件作为候选事件

2. 修改 `.skills/incident-capture/SKILL.md`：
   - 在"输入来源"部分增加 GUI 事件文件说明
   - 确保 GUI 事件能被正确识别和捕获

3. 创建 `incidents/gui_events/` 目录

4. 更新 `.gitignore` 文件

---

## Constraints / 约束条件

- 只能修改 Skills 的配置和文档，不能修改代码
- 保持现有技能的职责和结构不变
- GUI 事件应作为额外输入源，不影响现有输入处理

---

## Completion Criteria / 完成标准

1. incident-monitor 能检测到 `incidents/gui_events/` 中的新事件
2. incident-capture 能处理 GUI 事件文件并生成事件记录
3. `incidents/gui_events/` 目录已创建
4. `.gitignore` 已更新
5. Skills 配置更新符合项目规范
