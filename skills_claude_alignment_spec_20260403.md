# `.skills` 与 `.claude` 对齐规范

## 1. 结论

当前问题不是 `.claude` 标准缺失，而是 `.skills` 复写规则后发生漂移。

根因可归纳为三点：

1. `.claude/rules/` 本应是唯一规则真源
2. `.skills/` 不应定义规则，只应调用规则
3. 现有部分技能文件把自己写成了第二套规则系统

因此整改目标不是补充更多技能说明，而是让 `.skills` 回归“流程适配层”。

---

## 2. 正确分层

### 2.1 `.claude/rules/`

唯一规则真源，负责定义：

- ADP / 8D / HOTFIX
- 执行器分配
- 简化任务标准
- 编号与 `.sequence` 规则
- reviewer / tester 归档前置条件
- lock、归档、验证等正式约束

### 2.2 `.skills/`

流程适配层，负责：

- 判断何时调用哪个规则
- 调用前做依赖和存在性校验
- 协调执行顺序
- 产出执行报告

`.skills` 不得重复定义 `.claude` 已定义的规则正文。

### 2.3 `promptsRec/`

任务实例层，负责承载具体 prompt，不得反向覆盖仓库级规则。

---

## 3. 冲突清单

### P0

1. `prompt` 可覆盖 `.claude` 规则
2. Bug 类型用 `*_bug_*.md` 判断，而不是按 `10101-19999` 编号区间判断
3. `.skills` 与 `.claude` 关系设计错误，形成“复写规则”而不是“引用规则”
4. Lock 规则不一致，`Claude Code` 被豁免不上锁

### P1

5. 执行器分配漂移，重构等任务被错误上收给 `Claude Code`
6. 简化任务边界被技能层扩写
7. `archive/` 被重新引入流程判断，而不是只用 `.sequence`
8. ADP / 8D / HOTFIX 协议在技能层被二次复写
9. Prompt 生成缺少文档和文件存在性校验
10. 技能文档承担了主规则定义职责

---

## 4. 硬修复规则

以下规则应作为后续整改的统一准则：

### 规则 1

`.skills` 不得复写 `.claude/rules/` 的协议正文，只能引用规则文件及适用场景。

### 规则 2

任务类型识别只按编号区间，不按文件名片段。

- `00001-09999` → Feature
- `10101-19999` → Bug Fix
- `20101-29999` → Refactoring
- `30101-39999` → Testing

### 规则 3

执行器分配只按 `.claude/rules/05_task_convention.md`。

### 规则 4

简化任务标准只按 `.claude/rules/05_task_convention.md`，技能层不得扩写。

### 规则 5

任何进入 `RUNPROMPT` 链路的任务，执行前必须创建 `.lock`，不区分执行器。

### 规则 6

编号和执行顺序号只能从 `promptsRec/.sequence` 读取。

### 规则 7

生成 prompt 前必须校验：

- 引用规则文件存在
- 引用文档存在
- 目标代码文件存在
- 任务类型与编号一致
- 执行器与 `.claude` 一致
- 是否属于不应生成 prompt 的简化任务

### 规则 8

任何技能文件中不得出现“若 prompt 另有规定则以 prompt 为准”之类反向覆盖条款。

### 规则 9

归档判断只能按 `.claude` 的归档前置条件执行，不允许技能层自定义替代逻辑。

### 规则 10

`.claude/rules/` 更新后，`.skills` 只需要维护引用关系和前置校验，不应同步复制正文。

---

## 5. 逐文件整改建议

### 5.1 `.skills/prompt-task-runner/SKILL.md`

最高优先级。

必须修：

1. 删除“以 prompt 指示为准”条款
2. 删除 `*_bug_*.md` bug 判断逻辑
3. 改为按编号区间路由到对应规则
4. 删除 ADP / 8D / HOTFIX 正文复写
5. 删除或收缩依赖 `archive/` 的 follow-up 合并逻辑
6. 明确任何执行器执行前都要先上锁

### 5.2 `.skills/auto-task-generator/SKILL.md`

必须修：

1. 删除冲突的执行器定义
2. 删除扩写后的简化任务定义
3. 增加生成前存在性校验
4. 若任务属于简化任务，则拒绝生成正式 prompt

### 5.3 `.skills/self-healing-dev-loop/SKILL.md`

必须修：

1. 删除 `Executor = Claude Code` 不上锁规则
2. 删除重复定义的 reviewer / tester 正文
3. 保留 orchestration，移除主规则定义

### 5.4 `.skills/prompt-generator/SKILL.md`

必须修：

1. 删除大段 ADP / 8D / HOTFIX 复制内容
2. 改为引用 `.claude/rules/*.md`
3. 增加文档与目标文件存在性校验

---

## 6. 推荐整改顺序

1. `prompt-task-runner/SKILL.md`
2. `auto-task-generator/SKILL.md`
3. `self-healing-dev-loop/SKILL.md`
4. `prompt-generator/SKILL.md`

---

## 7. 验收标准

整改完成后，应满足以下条件：

1. `.skills` 中不再保留独立执行器规则表
2. `.skills` 中不再大段复写 ADP / 8D / HOTFIX
3. 所有任务类型按编号区间识别
4. 所有 RUNPROMPT 任务执行前都会创建 `.lock`
5. 新生成 prompt 不再引用失效文档或不存在文件
6. 简化任务不再错误生成正式 prompt
7. 任何技能文档都不能覆盖 `.claude` 规则

---

## 8. 实施建议

建议先完成 `.skills` 修复，再决定是否将本规范沉淀到 `docs/` 或 `.claude/`。

原因：

1. 当前主要问题在执行层
2. 先固化文档、后修执行，会把错误现状进一步制度化
3. 先修复，再固化，才能确保规范与执行一致

