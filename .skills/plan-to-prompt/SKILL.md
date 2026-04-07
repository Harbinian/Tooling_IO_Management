---
name: plan-to-prompt
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/01_workflow.md
  - .claude/rules/02_debug.md
  - .claude/rules/03_hotfix.md
  - .claude/rules/05_task_convention.md
  - .claude/rules/06_testing.md
version: 1.0.0
---

# 计划转提示词技能 / Plan-to-Prompt Skill

**规则约束**: 本技能在转换计划时，根据任务类型调用相应规则：
- 功能开发/重构 → `.claude/rules/01_workflow.md` (ADP)
- 测试任务 → `.claude/rules/06_testing.md`
- Bug 修复 → `.claude/rules/02_debug.md` (8D)
- 紧急修复 → `.claude/rules/03_hotfix.md` (HOTFIX)

## 目的 / Purpose

本技能将 Claude Code "计划模式"（Plan Mode）产生的对话结果转换为符合项目标准的可执行开发提示词。/ This skill converts Claude Code Plan Mode conversation results into executable development prompts that comply with project standards.

计划模式产生的对话结果具有独特的特点：/ Plan Mode results have unique characteristics:
- 更完整的上下文（Context）/ Complete context
- 明确的架构设计（Architecture）/ Explicit architecture design
- 具体的实现步骤（Implementation Steps）/ Specific implementation steps
- 约束条件（Constraints）/ Constraints
- 验证计划（Verification Plan）/ Verification plan

---

# 何时使用此技能 / When to Use This Skill

在以下情况下使用此技能：

Use this skill when:

- 用户提供了计划文件路径（如 `C:\Users\charl\.claude\plans\*.md`）
- 用户在对话中直接提供了计划内容
- 需要将计划转换为可执行的开发提示词
- 需要分析任务依赖关系并智能拆分任务

## 规则引用指南 / Rule Reference Guide

转换计划时，根据任务类型选择正确的规则文件：

| 任务类型 | 适用规则 | 说明 |
|----------|---------|------|
| 功能开发 / Feature | `.claude/rules/01_workflow.md` (ADP) | 四阶段开发流程 |
| Bug 修复 / Bug Fix | `.claude/rules/02_debug.md` (8D) | 问题解决协议 |
| 重构 / Refactoring | `.claude/rules/01_workflow.md` (ADP) | 架构设计优先 |
| 测试 / Testing | `.claude/rules/06_testing.md` | 测试任务规范 |
| 紧急修复 / Hotfix | `.claude/rules/03_hotfix.md` | 热修复流程 |

---

# 输入处理 / Input Processing

## 支持的输入格式

Supported input formats:

1. **计划文件路径**: 用户提供计划文件的完整路径
2. **对话上下文**: 用户在对话中直接提供计划内容

## 解析标准章节

Parse standard sections:

- Context / 背景
- Goal / 目标
- Implementation Steps / 实现步骤
- Constraints / 约束条件
- Verification Plan / 验证计划

---

# 任务识别 / Task Identification

分析计划内容，识别：

Analyze plan content to identify:

| 属性 | 说明 |
|------|------|
| **任务数量** | 计划包含多少个独立任务 |
| **任务类型** | Feature / Bug Fix / Refactoring / Testing |
| **执行器** | Gemini（前端）\| Codex（后端）\| Claude Code（架构）|
| **依赖关系** | 任务间的执行顺序 |
| **优先级** | P0 / P1 / P2 |

---

# 编号服务 / Numbering Service

获取提示词编号时，使用 `promptsRec/.sequence` 计数器文件：

| 任务类型 | 计数器 | 范围 |
|---------|--------|------|
| Feature | feature_next | 00001-09999 |
| Bug Fix | bugfix_next | 10101-19999 |
| Refactoring | refactor_next | 20101-29999 |
| Testing | test_next | 30101-39999 |

详见 `.claude/rules/05_task_convention.md` 的"计数器文件"章节。

---

# 智能拆分策略 / Smart Split Strategy

| 场景 | 策略 |
|------|------|
| 单一后端任务 | 单个 Codex 提示词 |
| 单一前端任务 | 单个 Gemini 提示词 |
| 前端+后端分离 | 拆分为两个提示词，后端依赖前置 |
| 多步骤重构 | 拆分为多个提示词，每步骤一个 |
| 复杂架构变更 | Claude Code 提示词 |

拆分因素：
- 涉及的代码模块数量
- 前端/后端/数据库的覆盖范围
- 是否有明确的步骤顺序
- 任务复杂度

---

# 提示词头部格式 / Prompt Header Format

每个生成的提示词必须以以下头部开头：

Primary Executor: <Agent>
Task Type: <Feature Development | Bug Fix | Refactoring | Testing>
Priority: <P0 | P1 | P2>
Stage: <Prompt Number>
Goal: <One-line description>
Dependencies: <"None" or list of prompt numbers that must complete first>
Execution: RUNPROMPT

---

# 必需章节 / Required Sections

每个生成的提示词必须包含以下章节：

- Context / 上下文
- Required References / 必需参考
- Core Task / 核心任务
- Required Work / 必需工作
- Constraints / 约束条件
- Completion Criteria / 完成标准

---

# 提示词编号规则 / Prompt Numbering Rules

提示词编号是严格定义的。

Prompt numbering is strictly defined.

| Range   | Category              |
|---------|----------------------|
| 00001–09999 | Feature Development  |
| 10101–19999 | Bug Fix / Security Fix |
| 20101–29999 | Refactoring / Tech Debt |
| 30101–39999 | Testing / Quality    |

---

# 输出要求 / Output Requirements

**AI 必须将生成的提示词实际写入 `promptsRec/active/` 目录，而不是仅输出内容摘要。**

The AI MUST actually write the generated prompt to the `promptsRec/active/` directory, not just output a content summary.

输出格式：

Output format:

文件名：promptsRec/active/<number>_<description>.md
执行模型：<Gemini | Codex | Claude Code>

Then output the full prompt content.

---

# 执行器选择规则 / Executor Selection Rules

| Executor     | Scope                                                        |
|--------------|--------------------------------------------------------------|
| Gemini       | Frontend tasks: UI, UX, component styling, page layout       |
| Codex        | Backend tasks: API, service logic, database queries           |
| Claude Code  | Architecture tasks: refactoring, cross-cutting concerns, RBAC design, workflow redesign, multi-file structural changes |

---

---

## 与相邻技能的边界 / Boundary with Adjacent Skills

| 维度 | 本技能 | prompt-generator |
|------|--------|-----------------|
| 输入 | 计划文件路径或对话内容（来自 Plan Mode） | 自由文本需求描述 |
| 输出 | 单个或批量提示词文件 | 单个提示词文件 |
| 使用场景 | 用户使用 Plan Mode 产生计划后 | 用户直接描述需求 |
| 与 prompt-generator 关系 | 下游：plan-to-prompt 产生的提示词可由 prompt-generator 精化 | 上游：prompt-generator 可直接生成提示词 |

---

# 约束条件 / Constraints

AI 不得：

The AI must NOT:

- 仅输出提示词内容而不生成实际文件
- 生成不完整的提示词
- 跳过必需章节
- 无正当理由重新设计稳定架构
- 假设数据库架构
- 不检查就假设后端 API
- 生成超出编号规则的提示词
- 跳过优先级声明
- 跳过依赖声明（当有依赖时）

---

# 完成标准 / Completion Criteria

生成的提示词只有在以下情况下才被视为有效：

1. 遵循提示词格式
2. 遵守编号规则
3. 包含所有必需章节
4. 包含具体的验收测试
5. 正确声明依赖关系
6. 可以由 RUNPROMPT 直接执行

---

# 会话结束规则 / Session End Rule

**生成提示词后，必须退出计划模式，会话结束。**

生成完所有提示词后，AI 必须：
1. 调用 `ExitPlanMode` 退出计划模式
2. 不进行任何额外的解释或说明
3. 等待用户下一步指令

This is the final step. After generating all prompts, exit plan mode immediately and end the conversation.
