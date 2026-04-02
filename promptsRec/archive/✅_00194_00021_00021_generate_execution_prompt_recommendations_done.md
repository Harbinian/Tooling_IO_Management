Primary Executor: Claude Code
Task Type: Feature Development
Priority: P2
Stage: 00021
Goal: 基于当前仓库状态生成下一步最值得执行的标准化提示词建议
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

当前仓库存在多个 active prompt、流程资产和并行中的开发/测试上下文，需要生成一份面向仓库操作者的“下一步执行建议”。

本任务不是直接修复某个单点 Bug，而是：

1. 审视当前 `promptsRec/active/` 中的任务状态
2. 审视 `.sequence` 编号分配状态
3. 审视最近代码与测试变更是否暴露新的执行机会或风险
4. 生成 1 到 3 个最值得继续推进的标准化提示词建议

输出必须适合后续人工选择并直接进入 `RUNPROMPT` 流程，不能是泛泛分析。

---

## Required References / 必需参考

1. `.skills/prompt-generator/SKILL.md`
2. `.claude/rules/01_workflow.md`
3. `.claude/rules/05_task_convention.md`
4. `promptsRec/.sequence`
5. `promptsRec/active/`
6. `docs/API_SPEC.md`
7. `docs/DB_SCHEMA.md`
8. `docs/RBAC_PERMISSION_MATRIX.md`
9. `docs/ARCHITECTURE.md`

如发现当前建议触及 Bug 修复、热修或测试规划，应同时加载：

- `.claude/rules/02_debug.md`
- `.claude/rules/03_hotfix.md`

---

## Core Task / 核心任务

使用仓库的提示词生成规范，产出“下一步最值得执行的任务建议”。

必须完成以下分析：

1. 检查 `promptsRec/active/` 当前未完成任务，识别是否已有待执行高优先级项
2. 检查近期代码和测试变更暴露出的缺口，例如：
   - 缺少回归测试
   - 文档与实现不一致
   - 前后端联调未完成
   - RBAC、设置页、系统配置、工作流状态等关键链路仍有验证空白
3. 判断哪些任务适合：
   - 立即生成正式 prompt
   - 暂缓，等待依赖完成
   - 合并到现有 active prompt，而不是新增 prompt

最终输出按优先级排序的建议列表，并在适合时直接给出完整 prompt 正文。

---

## Required Work / 必需工作

1. 读取并分析 `.sequence`，不得通过扫描 archive 推断编号
2. 读取当前 `promptsRec/active/`，识别冲突、重复或依赖关系
3. 最多提出 3 个候选任务，且每个候选任务必须包含：
   - 建议标题
   - 任务类型
   - 优先级
   - 推荐执行器
   - Dependencies
   - 为什么现在值得做
   - 涉及文件/模块
4. 对“最推荐”的候选任务，若适合立即执行，生成完整标准 prompt，格式必须符合仓库规范：
   - Primary Executor
   - Task Type
   - Priority
   - Stage
   - Goal
   - Dependencies
   - Execution: RUNPROMPT
   - Context
   - Required References
   - Core Task
   - Required Work
   - Constraints
   - Completion Criteria
5. 若当前不适合新增 prompt，必须明确说明阻塞原因，并给出后续动作建议
6. 将最终建议写入运行报告，确保此次 RUNPROMPT 有流程资产沉淀

---

## Constraints / 约束条件

- 禁止脱离真实仓库状态臆测任务
- 禁止扫描 `archive/` 反推新编号
- 禁止生成空泛“优化一下”“完善体验”类建议
- 如果建议跨前后端，优先拆成具备依赖关系的多个 prompt
- 必须显式判断是否应该复用现有 active prompt，而不是盲目新增
- 若涉及 API、权限或 schema，必须与 `docs/` 权威文档核对
- 输出面向人类快速决策，优先结论，不展示大段实现细节

---

## Completion Criteria / 完成标准

1. 至少输出 1 个、最多输出 3 个真实可执行的候选任务建议
2. 每个建议都包含任务类型、优先级、执行器、依赖、价值判断
3. 最推荐任务在适合时提供完整可落盘 prompt 正文
4. 不出现编号违规、执行器误配、依赖缺失或章节缺失
5. 输出结果可被仓库操作者直接用于决定下一步 `RUNPROMPT`
