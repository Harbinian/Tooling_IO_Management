# 需求收集 / REQUIREMENT HARVEST

---

## 目的 / Purpose

通过结构化的5W2H问答流程，引导用户明确需求，生成标准化的需求文档。 / Guide users through a structured 5W2H questioning process to clarify requirements and generate standardized requirement documents.

此技能不直接实现功能，只收集和整理需求。 / This skill does NOT implement features — it only collects and organizes requirements.

---

## 规则约束 / Rule Constraints

**本技能受以下规则约束，必须遵循：**

1. **提示词格式规范**：提示词生成必须遵循 `.claude/rules/05_task_convention.md` 及 `auto-task-generator/SKILL.md` 中定义的格式标准
2. **编号约定**：提示词编号必须来自 `promptsRec/.sequence` 计数器
3. **执行者分配**：根据任务类型确定执行者（详见 `auto-task-generator/SKILL.md`）

> **重要**：功能开发提示词 (00001-09999) 必须使用 **ADP 四阶段章节**（Phase 1-4），而非自定义的 `Core Task` 等章节。

---

## 5W2H 框架 / 5W2H Framework

| 维度 | 问题 | 目的 |
|------|------|------|
| What | 要做什么？ | 明确核心需求和功能 |
| Why | 为什么要做？ | 理解动机和价值 |
| Who | 谁来做？谁受影响？ | 确定执行者和用户 |
| When | 什么时候需要？ | 确定优先级和时间线 |
| Where | 在哪里使用？ | 确定使用场景 |
| How | 怎么做？ | 确定实现方式 |
| How Much | 需要多少资源？ | 确定成本和范围 |

---

## 输入 / Inputs

用户可能以以下形式提出需求：

- 简单描述（如"需要一个订单统计功能"）
- 详细的问题描述
- 现有的痛点或改进建议
- 用户的解决方案想法

---

## 问答流程 / Questioning Flow

### 阶段 1: What - 核心需求

**目标**：明确要做什么

关键问题：

1. **核心功能是什么？** / What is the core feature?
   - 用户想要实现什么具体功能？
   - 这个功能解决什么问题？

2. **期望的输入是什么？** / What are the inputs?
   - 用户提供什么数据？
   - 数据来源是什么？

3. **期望的输出是什么？** / What are the outputs?
   - 用户期望看到什么结果？
   - 结果以什么形式呈现？

**探索性问题**：
- 能具体描述一下这个功能吗？
- 有没有具体的例子说明这个功能应该如何工作？

---

### 阶段 2: Why - 动机与价值

**目标**：理解为什么需要这个功能

关键问题：

1. **为什么需要这个功能？** / Why is this needed?
   - 当前的痛点是什么？
   - 现有方案有什么问题？

2. **这个功能带来什么价值？** / What value does it bring?
   - 效率提升？
   - 错误减少？
   - 用户体验改善？

3. **成功标准是什么？** / What defines success?
   - 如何衡量这个功能是否达到预期？

---

### 阶段 3: Who - 角色与用户

**目标**：确定执行者和受影响者

关键问题：

1. **谁会使用这个功能？** / Who will use this feature?
   - 角色：班组长？保管员？管理员？
   - 使用频率：高/中/低

2. **谁来开发和测试？** / Who will develop and test?
   - 需要什么技能？
   - 是否有现有团队成员负责？

3. **谁会受到影响？** / Who will be impacted?
   - 直接用户
   - 间接影响的工作流

---

### 阶段 4: When - 时间线

**目标**：确定优先级和时间要求

关键问题：

1. **什么时候需要完成？** / When is the deadline?
   - 硬性截止日期？
   - 可协商的时间范围？

2. **什么时候可以开始？** / When can development start?
   - 是否有前置依赖？
   - 资源什么时候可用？

3. **使用频率是什么？** / What is the usage frequency?
   - 实时？定期？一次性？

---

### 阶段 5: Where - 使用场景

**目标**：确定使用环境和场景

关键问题：

1. **在哪里使用？** / Where will this be used?
   - 生产环境？
   - 特定部门/场景？

2. **与其他系统的集成？** / Integration with other systems?
   - 飞书通知？
   - 外部数据库？
   - API 调用？

3. **有什么约束条件？** / What are the constraints?
   - 性能要求？
   - 安全要求？
   - 合规要求？

---

### 阶段 6: How - 实现方式

**目标**：确定实现方法

关键问题：

1. **你认为应该怎么实现？** / How do you think it should be implemented?
   - 用户是否有具体的实现思路？

2. **有没有参考的系统或功能？** / Are there reference systems?
   - 类似功能在哪里见过？

3. **技术栈偏好？** / Technology preferences?
   - 后端：Flask + SQL Server？
   - 前端：Vue 3 + Element Plus？

---

### 阶段 7: How Much - 资源与范围

**目标**：确定成本和范围

关键问题：

1. **预算范围是多少？** / What is the budget range?
   - 时间预算？
   - 开发资源预算？

2. **范围边界是什么？** / What is in scope / out of scope?
   - 必须包含什么？
   - 明确不包括什么？

3. **优先级是什么？** / What is the priority?
   - P0（核心功能）？
   - P1（重要但可延后）？
   - P2（Nice to have）？

---

## 输出 / Outputs

### 1. 需求文档 / Requirement Document

生成文件：`docs/REQUIREMENTS/<需求名称>_requirements.md`

文档结构：

```markdown
# 需求：<需求名称>

## 基本信息 / Basic Information
- 需求编号：REQ-YYYYMMDD-NNN
- 创建日期：YYYY-MM-DD
- 状态：收集中 / 已完善 / 已批准

## 5W2H 分析 / 5W2H Analysis

### What - 核心需求
**功能描述**：
<详细描述>

**输入**：
<输入数据>

**输出**：
<输出结果>

### Why - 动机与价值
**业务背景**：
<为什么需要这个功能>

**预期价值**：
<带来的价值>

**成功标准**：
<如何衡量成功>

### Who - 角色与用户
**主要用户**：
<用户角色>

**开发负责人**：
<开发者>

**受影响者**：
<间接受影响的流程/人员>

### When - 时间线
**期望完成时间**：
<日期>

**使用频率**：
<频率>

**优先级**：
<P0/P1/P2>

### Where - 使用场景
**使用环境**：
<环境>

**集成需求**：
<与其他系统的集成>

**约束条件**：
<约束>

### How - 实现方式
**建议实现方式**：
<用户建议>

**参考系统**：
<参考>

**技术栈**：
<技术选择>

### How Much - 资源与范围
**范围**：
- [ ] 包含：<功能点>
- [ ] 不包含：<排除的功能>

**资源需求**：
<开发时间/人力>

## 待确认问题 / Open Questions
- [ ] <问题1>
- [ ] <问题2>

## 验收标准 / Acceptance Criteria
1. <标准1>
2. <标准2>

## 关联文档 / Related Documents
- <PRD.md>
- <API_SPEC.md>
```

### 2. 后续提示词 / Follow-up Prompt

根据需求类型，生成对应的提示词。**格式必须遵循 `auto-task-generator/SKILL.md` 中的定义。**

| 需求类型 | 提示词编号 | 必须章节 |
|---------|-----------|---------|
| 功能开发 (00001-09999) | 00001-09999 | ADP 四阶段（Phase 1-4）+ Header + Context + Required References + Constraints + Completion Criteria |
| Bug修复 (10101-19999) | 10101-19999 | 8D 八阶段（D1-D8）+ Header + Context + Required References + Constraints + Completion Criteria |
| 重构 (20101-29999) | 20101-29999 | ADP 四阶段（Phase 1-4）+ Header + Context + Required References + Constraints + Completion Criteria |
| 测试 (30101-39999) | 30101-39999 | Test Scope + Test Strategy + Test Cases + Pass Criteria + Test Artifacts |

**禁止使用以下章节名称**：
- ❌ `Core Task / 核心任务` - 功能开发应使用 `Phase 1-4`
- ❌ `Required Work / 必需工作` - 应整合到 `Phase 4` 中
- ❌ `Acceptance Tests / 验收测试` - 应使用 `Completion Criteria`

**Header 格式（所有类型必需）**：
```
Primary Executor: <Agent>
Task Type: <Feature Development | Bug Fix | Refactoring | Testing>
Priority: <P0 | P1 | P2>
Stage: <5-digit Prompt Number>
Goal: <One-line description>
Dependencies: <"None" or list of prompt numbers>
Execution: RUNPROMPT
```

---

## 问答策略 / Questioning Strategy

### 何时使用完整5W2H

对以下情况使用完整的5W2H分析：
- 新功能开发
- 系统重构
- 较大的改进建议

### 何时简化

对以下情况可以简化：
- 明确的小bug修复 → 只问 What/Why/When
- 参数调整 → 只问 What/How Much
- 文档更新 → 只问 What/Why

### 追问技巧

当用户回答模糊时，使用以下追问：

1. **具体化**："能举个例子吗？"
2. **量化**："大概是多少？"
3. **边界**："什么情况下不适用？"
4. **优先级**："最重要的是哪个？"

---

## 约束 / Constraints

此技能严禁：

- 不过问用户就自行决定需求细节
- 修改现有代码
- 跳过用户确认直接生成提示词
- 使用拼音命名
- **生成不符合规范的提示词格式**（详见 `auto-task-generator/SKILL.md`）
- **跳过必需的提示词章节**（如 Phase 1-4、Header 等）

---

## 完成标准 / Completion Criteria

技能完成当且仅当：

1. [ ] 用户回答了所有相关5W2H问题
2. [ ] 生成的需求文档包含所有7个维度
3. [ ] 用户确认需求文档准确
4. [ ] 生成了对应的后续提示词（如需要）
5. [ ] 提示词遵循编号约定（00001-09999 / 10101-19999 / 20101-29999 / 30101-39999）
6. [ ] **提示词格式符合 `auto-task-generator/SKILL.md` 规范**（包含正确的章节标题）

---

## 与其他技能的关系 / Relationship with Other Skills

| 技能 | 关系 |
|------|------|
| `auto-task-generator` | 需求收集完成后，生成对应的任务提示词 |
| `prompt-task-runner` | 需求明确后执行实现 |
| `bug-triage` | Bug类需求使用bug-triage流程 |
| `plan-to-prompt` | 复杂需求可先用plan-to-prompt做架构设计 |

---

## 触发条件 / Triggers

此技能在以下情况触发：

- 用户表达模糊需求（如"想要一个XXX功能"）
- 用户提出改进建议
- 用户报告问题但不清楚是bug还是需求
- 项目启动新功能的讨论

不触发此技能：
- 明确的bug报告（用 bug-triage）
- 已经有明确方案的需求
- 简单的参数问题
