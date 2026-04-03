# `.skills` 与 `.claude` 冲突清单

## 1. 说明

本清单用于盘点 `E:\CA001\Tooling_IO_Management\.skills` 与 `E:\CA001\Tooling_IO_Management\.claude` 之间的规则冲突、流程漂移与执行失真问题。

结论先行：

- 问题不是 `.claude` 标准不明确
- 问题是 `.skills` 在执行层重复定义了一套近似规则
- 这些技能文档与 `.claude` 真源规则发生了优先级反转、触发条件错误、执行器漂移与流程分叉

---

## 2. 审查范围

本次重点检查以下文件：

- `.claude/rules/00_core.md`
- `.claude/rules/01_workflow.md`
- `.claude/rules/02_debug.md`
- `.claude/rules/05_task_convention.md`
- `.skills/prompt-task-runner/SKILL.md`
- `.skills/auto-task-generator/SKILL.md`
- `.skills/self-healing-dev-loop/SKILL.md`
- `.skills/prompt-generator/SKILL.md`

---

## 3. 冲突清单

### 3.1 规则优先级被反转

**冲突点**

` .skills/prompt-task-runner/SKILL.md ` 写有类似“如果提示词中明确指定了不同规则或流程，以提示词中的指示为准”的条款。

**对应真源规则**

- `.claude/rules/00_core.md`
- `.claude/rules/05_task_convention.md`

**问题性质**

这是优先级设计错误。仓库级规则本应高于具体 prompt，但该技能文件允许 prompt 反向覆盖项目规则。

**影响**

- 不合规 prompt 也可能被执行
- 项目标准失去约束力
- 审核节点可能被绕开

**建议等级**

P0，必须修复

---

### 3.2 Bug 提示词识别条件错误

**冲突点**

` .skills/prompt-task-runner/SKILL.md ` 使用 `*_bug_*.md` 判断 bug 提示词。

**对应真源规则**

- `.claude/rules/05_task_convention.md` 规定 bug 类型以编号区间 `10101-19999` 判定

**问题性质**

命名匹配逻辑错误。仓库实际常见文件名为：

- `10190_fix_inspection_api_500.md`
- `10193_fix_login_api_401_inconsistency.md`
- `10194_fix_rbac_permission_mismatch.md`

这些都不满足 `*_bug_*.md`。

**影响**

- Bug prompt 可能不按 8D 协议执行
- D3/D5/D6 reviewer 节点可能被漏检
- 归档判断可能失真

**建议等级**

P0，必须修复

---

### 3.3 执行器分配与 `.claude` 漂移

**冲突点**

以下技能文件对执行器规则进行了二次定义：

- `.skills/prompt-task-runner/SKILL.md`
- `.skills/auto-task-generator/SKILL.md`
- `.skills/self-healing-dev-loop/SKILL.md`

其中多处把重构任务写成“始终由 Claude Code 执行”。

**对应真源规则**

`.claude/rules/05_task_convention.md` 规定：

- 普通 Bug 修复默认 `Codex`
- 普通重构默认 `Codex`
- 测试任务默认 `Claude Code`
- 简化任务由 `Claude Code`

**问题性质**

技能文档在重写执行器规则，而不是引用真源。

**影响**

- 任务分配与仓库制度脱节
- 正常应交给 Codex 的任务被上收
- 执行策略不一致，导致提示词生成和实际执行不一致

**建议等级**

P1，高优先级修复

---

### 3.4 简化任务边界被技能层扩写

**冲突点**

` .skills/auto-task-generator/SKILL.md ` 将“不涉及架构变更的 bug 修复”也纳入简化任务。

**对应真源规则**

`.claude/rules/05_task_convention.md` 中简化任务定义较窄，主要包括：

- 参数错误
- 调用错误
- 签名修正
- 文档同步
- 单文件单函数修复

**问题性质**

技能文档扩大了简化任务的适用范围。

**影响**

- 应走标准 bug 流程的任务被错误降级
- 不该跳过 prompt 的任务被直接执行
- 8D 流程和 reviewer 节点容易缺失

**建议等级**

P1，高优先级修复

---

### 3.5 `archive` 被重新引入为流程判断依据

**冲突点**

` .skills/prompt-task-runner/SKILL.md ` 多处要求扫描 `promptsRec/archive/`：

- 查找 follow-up task
- 进行归档合并
- 读取原归档内容再追加

**对应真源规则**

`.claude/rules/05_task_convention.md` 明确：

- 编号来源只能是 `promptsRec/.sequence`
- 禁止扫描 `archive` 推断编号

**问题性质**

虽然技能文档不一定直接用 `archive` 分配新编号，但它把 `archive` 引入了流程判断核心路径。

**影响**

- 流程状态判断复杂化
- follow-up 合并逻辑可能污染归档真相
- 编号治理和归档治理容易耦合失控

**建议等级**

P1，高优先级修复

---

### 3.6 Lock 规则与仓库要求不一致

**冲突点**

` .skills/self-healing-dev-loop/SKILL.md ` 写有：

- `Executor = Claude Code` 时不创建 lock 文件

**对应真源规则**

仓库总规范明确要求执行 prompt 前先创建 `.lock`，避免并发重复执行。

**问题性质**

这是并发保护规则不一致。

**影响**

- Claude Code 直接执行时可能绕过锁保护
- 多执行器环境中容易出现抢占和重复处理

**建议等级**

P0，必须修复

---

### 3.7 ADP / 8D / HOTFIX 在技能层被二次复写

**冲突点**

以下技能文件均包含一套摘要版或扩写版协议：

- `.skills/prompt-task-runner/SKILL.md`
- `.skills/prompt-generator/SKILL.md`
- `.skills/self-healing-dev-loop/SKILL.md`

**对应真源规则**

- `.claude/rules/01_workflow.md`
- `.claude/rules/02_debug.md`
- `.claude/rules/03_hotfix.md`

**问题性质**

技能文档不只是引用规则，而是在维护“第二套协议文本”。

**影响**

- `.claude` 一旦更新，`.skills` 很容易不同步
- 使用者会看到两套相似但不完全一致的标准
- 执行时容易以旧技能文档为准

**建议等级**

P1，高优先级修复

---

### 3.8 提示词生成缺少“真实落点存在性校验”

**冲突点**

` .skills/prompt-generator/SKILL.md ` 与 ` .skills/auto-task-generator/SKILL.md ` 强调结构化生成，但未把“权威文档存在性检查”和“目标文件存在性检查”设为前置硬校验。

**对应真源规则**

- `.claude/rules/00_core.md`
- `.claude/rules/05_task_convention.md`

**问题性质**

生成逻辑强调模板完整性，但缺少仓库现实校验。

**影响**

- 容易生成引用失效文档的 prompt
- 容易生成落点不存在的执行要求
- 容易出现“形式正确、内容失真”的提示词

**建议等级**

P1，高优先级修复

---

### 3.9 技能文档承担了不该承担的“规则主定义”职责

**冲突点**

`.skills` 多个技能文件中大量使用“必须”“始终”“不得”等主规则式语句。

**对应真源规则**

仓库规则真源应为 `.claude/rules/`

**问题性质**

技能文档应是调用说明，不应成为规则主定义层。

**影响**

- 模型容易把技能文件当成另一套正式规范
- 维护责任边界不清晰
- 规则冲突难以及时收敛

**建议等级**

P1，高优先级修复

---

### 3.10 `.skills` 与 `.claude` 的关系设计错误

**冲突点**

当前关系是：

- `.claude` 定义规则
- `.skills` 又复写规则

**正确关系应为**

- `.claude` 负责定义规则
- `.skills` 负责说明何时调用哪个规则、如何执行、产出什么

**问题性质**

架构分层错误。

**影响**

- 维护成本翻倍
- 漂移不可避免
- 技能执行长期偏离仓库标准

**建议等级**

P0，必须修复

---

## 4. 风险总结

如果不修复上述冲突，持续风险包括：

1. 生成并执行不合规 prompt
2. Bug 任务绕过 8D 审核节点
3. 重构和测试任务执行器持续错配
4. `.sequence` 与归档治理持续失真
5. 多执行器并发下出现锁保护缺失
6. 新增技能继续复制旧规则，冲突面不断扩大

---

## 5. 总结结论

本次检查确认：

1. `.claude` 规则本身是明确的
2. `.skills` 不是“没读规则”，而是“复写规则后产生漂移”
3. 修复重点不在补充 `.claude`，而在收缩 `.skills` 的规则定义权
4. 最合理的方向是让 `.skills` 回归为“规则调用器”，而不是“规则再定义器”

