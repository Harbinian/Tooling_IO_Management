# `.skills` 与 `.claude` 规则冲突诊断与整改记录

**日期**: 2026-04-03
**问题**: `.skills` 技能文件重复定义 `.claude/rules/` 中的规则，导致优先级反转、执行器漂移、协议正文失同步
**状态**: 已整改

---

## 1. 根因

`.claude/rules/` 是仓库规则唯一真源。`.skills` 技能文件本应是"规则调用层"，但在实际执行中演变成了"规则再定义层"，产生了以下问题：

- 优先级反转：prompt 可反向覆盖项目规则
- 执行器分配与真源不一致
- Bug 识别用文件名 `*_bug_*.md` 而非编号区间 `10101-19999`
- ADP/8D/HOTFIX 协议被复制到技能层，与真源脱节
- Claude Code 执行时绕过 lock 保护

---

## 2. 冲突清单（已整改）

| # | 冲突点 | 等级 | 涉及文件 | 整改方式 |
|---|--------|------|----------|----------|
| 1 | prompt 可覆盖 `.claude` 规则 | P0 | prompt-task-runner | 删除反向覆盖条款 |
| 2 | Bug 用 `*_bug_*.md` 而非 `10101-19999` 区间判断 | P0 | prompt-task-runner, bug-triage, pipeline-dashboard | 改为按编号区间判断 |
| 3 | Claude Code 不上锁 | P0 | self-healing-dev-loop | 统一所有执行者必须上锁 |
| 4 | 执行器分配与真源漂移 | P1 | prompt-task-runner, auto-task-generator, self-healing-dev-loop | 改为引用 `.claude/rules/05_task_convention.md` |
| 5 | 简化任务边界被技能层扩写 | P1 | auto-task-generator | 删除扩写内容，引用真源 |
| 6 | ADP/8D/HOTFIX 协议在技能层二次复写 | P1 | prompt-task-runner, prompt-generator, self-healing-dev-loop | 删除正文，改为引用真源文件 |
| 7 | Prompt 生成缺少存在性校验 | P1 | auto-task-generator, prompt-generator | 增加生成前硬校验 |
| 8 | 技能文档承担"主规则定义"职责 | P1 | 全部技能文件 | 降为流程适配层 |
| 9 | requirement-harvest 维护了弱化版 prompt 协议并错误吸收简化任务 | P1 | requirement-harvest | 收缩为需求收集与分流层，后续 prompt 一律委托真源生成器 |

---

## 3. 整改后的规则真源层级

### 层 1：规则真源层（`.claude/rules/`）

- 定义所有标准
- 定义审核门槛
- 定义执行器映射
- 定义归档前提
- 定义编号与计数器规则

### 层 2：技能编排层（`.skills/`）

- 检测使用场景
- 选择调用哪条规则
- 串联步骤
- 执行前做存在性和依赖校验
- 执行后生成报告

### 层 3：提示词实例层（`promptsRec/`）

- 承载具体任务实例
- 不得反向定义仓库级规则

---

## 4. 硬规则（整改后）

1. `.skills` 不得复写 `.claude/rules` 的协议正文，只能引用文件路径与适用场景
2. 任务类型识别只按编号区间，不按文件名片段
3. 执行器分配只按 `.claude/rules/05_task_convention.md`
4. 简化任务标准只按 `.claude/rules/05_task_convention.md`
5. 任何进入 RUNPROMPT 链路的任务，执行前必须创建 `.lock`
6. 编号和执行顺序号只允许从 `promptsRec/.sequence` 读取
7. 生成 prompt 前必须校验：引用路径存在、目标文件存在、执行器匹配、任务分类匹配
8. 任何技能文件不得出现"若 prompt 中另有规定则以 prompt 为准"
9. 归档判断只按 `.claude` 归档前置条件执行
10. 如 `.claude/rules` 更新，`.skills` 只能检查引用路径是否仍有效
11. `requirement-harvest` 只负责需求澄清与结构化输入，不维护独立 prompt 章节模板
12. 测试任务提示词在技能层同样不得偏离 `.claude/rules/01_workflow.md` 的 ADP 真源

---

## 5. 验收标准

- [x] `.skills` 中不再出现独立执行器规则表
- [x] `.skills` 中不再出现 ADP/8D/HOTFIX 正文大段复写
- [x] Bug、feature、refactor、testing 类型均按编号区间识别
- [x] Claude Code 进入 RUNPROMPT 时也会创建 `.lock`
- [x] 生成新 prompt 前会拒绝失效文档引用
- [x] 简化任务不会再错误生成正式 prompt
- [x] 任意技能文档都不能覆盖 `.claude` 规则
- [x] requirement-harvest 不再把简化任务错误升级为正式 prompt
- [x] requirement-harvest 不再维护独立测试任务章节模板

---

## 6. 受影响文件清单

| 文件 | 整改内容 |
|------|----------|
| `.skills/prompt-task-runner/SKILL.md` | 删除反向覆盖条款、删除执行器规则表、删除协议正文、删除自制图标规则 |
| `.skills/auto-task-generator/SKILL.md` | 删除执行器规则表、删除简化任务扩写、增加生成前存在性校验 |
| `.skills/self-healing-dev-loop/SKILL.md` | 删除 Claude Code 不上锁例外、删除执行器规则表、简化锁记录逻辑 |
| `.skills/prompt-generator/SKILL.md` | 删除协议正文、删除执行器规则表、增加生成前存在性校验 |
| `.skills/bug-triage/SKILL.md` | 删除 `*_bug_*.md` 文件名匹配，改为按编号区间 |
| `.skills/pipeline-dashboard/SKILL.md` | 删除文件名片段匹配，改为按编号区间 |
| `.skills/requirement-harvest/SKILL.md` | 删除弱化版 prompt 模板定义、改为委托 auto-task-generator、修正简化任务与测试任务分流 |
