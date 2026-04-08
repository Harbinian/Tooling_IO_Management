# 技能依赖关系图 / Skill Dependency Map

---

## 技能列表

| 技能 | Executor | 类型 | 说明 |
|------|---------|------|------|
| `auto-task-generator` | Claude Code | 普通 | 自动任务生成 |
| `bug-triage` | Claude Code | 普通 | Bug 分类 |
| `codex-rectification-log` | Claude Code | 普通 | Codex 纠正日志 |
| `dev-inspector` | Claude Code | 普通 | 开发检查器 |
| `frontend-design` | Claude Code | 普通 | 前端设计 |
| `human-e2e-tester` | Claude Code | 普通 | 人工 E2E 测试 |
| `incident-capture` | Claude Code | 普通 | 事件捕获 |
| `incident-monitor` | Claude Code | 普通 | 事件监控 |
| `pipeline-dashboard` | Claude Code | 普通 | 流水线仪表盘 |
| `plan-to-prompt` | Claude Code | 普通 | 计划转提示词 |
| `prompt-generator` | Claude Code | 普通 | 提示词生成 |
| `prompt-task-runner` | Claude Code | 普通 | 提示词任务执行 |
| `release-precheck` | Claude Code | 普通 | 发布预检 |
| `repo-context-firewall` | Claude Code | 普通 | 仓库上下文防火墙 |
| `requirement-harvest` | Claude Code | 普通 | 需求收集 |
| `scripted-e2e-builder` | Codex | 普通 | 脚本化 E2E 构建 |
| `self-healing-dev-loop` | Claude Code | 普通 | 自愈开发循环 |
| `skill-audit-and-fix` | Claude Code | **元技能** | 技能审查与修复 |
| `token-context-optimizer` | Claude Code | 普通 | Token 上下文优化 |

---

## 依赖关系

| 技能 | depends_on | 说明 |
|------|-----------|------|
| `self-healing-dev-loop` | `dev-inspector` | 依赖开发检查器发现问题后触发 |
| `scripted-e2e-builder` | `human-e2e-tester` | 依赖人工测试结果构建自动化脚本 |
| `incident-capture` | `incident-monitor` | 被动接收监控发现的事件 |

---

## 调用链路

### 主开发链路

```
requirement-harvest → plan-to-prompt → prompt-generator → auto-task-generator
                                                        ↓
                                              prompt-task-runner
                                                        ↓
                                                 [执行开发]
                                                        ↓
                                                 self-healing-dev-loop（如需自愈）
                                                        ↓
                                                 human-e2e-tester
                                                        ↓
                                              release-precheck
```

### 事件处理链路

```
incident-monitor → incident-capture → bug-triage → auto-task-generator
```

### 辅助链路

- `dev-inspector` → 发现问题 → `auto-task-generator`
- `frontend-design` → 前端设计
- `repo-context-firewall` → 上下文优化
- `token-context-optimizer` → Token 优化
- `codex-rectification-log` → Codex 纠正记录
- `pipeline-dashboard` → 流水线状态监控
- `skill-audit-and-fix` → 技能文件维护（元技能）

---

## 元技能

| 技能 | 说明 | auto_invoke |
|------|------|-------------|
| `skill-audit-and-fix` | 技能审查与修复 | false |

元技能不列入自身审查范围，不形成循环依赖。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-07 | 初始版本 |
