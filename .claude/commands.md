# Claude Code Commands

本文件定义了项目中可用的 slash commands。

---

## 技能命令 / Skill Commands

| 命令 / Command | 描述 / Description |
|--------------|-------------------|
| /pipeline-dashboard | 显示流水线状态并推荐下一个任务 / Show pipeline status and recommend next task |
| /prompt-task-runner | 执行提示词任务 / Execute prompt task |
| /release-precheck | 执行发布预检 / Execute release precheck |
| /bug-triage | Bug 分类和优先级排序 / Bug triage and priority sorting |
| /incident-capture | 捕获运行时事件 / Capture runtime incidents |
| /incident-monitor | 监控事件 / Monitor incidents |
| /prompt-generator | 生成提示词 / Generate prompts |
| /auto-task-generator | 自动生成任务 / Auto-generate tasks |
| /plan-to-prompt | 将计划转换为提示词 / Convert plan to prompts |
| /dev-inspector | 检查代码 / Inspect code |
| /self-healing-dev-loop | 自愈开发循环 / Self-healing dev loop |

---

## 使用方法 / Usage

在 Claude Code 中输入 `/` 加上命令名称即可调用对应技能。

Type `/` followed by the command name to invoke the corresponding skill.

示例 / Examples:

```
/pipeline-dashboard
/prompt-task-runner
/release-precheck
```

---

## 技能位置 / Skill Location

所有技能位于: / All skills are located at:

- `C:\Users\charl\.claude\skills\` (集中维护)

---

## 更多信息 / More Information

参见 / See also:

- `docs/ARCHITECTURE_INDEX.md` - 架构索引
