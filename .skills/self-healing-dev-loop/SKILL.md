---
name: self-healing-dev-loop
executor: Claude Code
auto_invoke: false
depends_on:
  - dev-inspector
triggers: []
rules_ref:
  - .claude/rules/02_debug.md
  - .claude/rules/03_hotfix.md
  - .claude/rules/01_workflow.md
  - .claude/rules/05_task_convention.md
version: 1.0.0
---

# 自愈开发循环技能 / Self Healing Dev Loop Skill

**规则约束**: 本技能协调问题修复时，根据问题类型调用相应规则：
- Bug 修复问题 (10101-19999) → `.claude/rules/02_debug.md` (8D 问题解决协议)
- 生产环境紧急修复 → `.claude/rules/03_hotfix.md` (热修复 SOP)
- 功能开发/重构/测试 → `.claude/rules/01_workflow.md` (ADP 开发协议)
- 任务编号约定 → `.claude/rules/05_task_convention.md`

---

## 强制审核机制 / MANDATORY Review Mechanism

**红线警告**: 以下审核节点不可跳过：

### Bug 修复 D3/D5/D6 评分审核

Bug 修复任务（10101-19999）在 D3、D5、D6 阶段**必须**触发 reviewer 评分审核：

```
D3 完成 → SendMessage(to: "reviewer", type: "plan_approval_request")
        → reviewer 回复评分结果
        → 收到全部维度达标后才能继续 D4

D5 完成 → SendMessage(to: "reviewer", type: "plan_approval_request")
        → reviewer 回复评分结果
        → 收到全部维度达标后才能继续 D6

D6 完成 → SendMessage(to: "reviewer", type: "plan_approval_request")
        → reviewer 回复评分结果
        → 收到全部维度达标后才能继续 D7
```

**评分维度与门槛**（来自 `.claude/rules/02_debug.md`）：

| 维度 | 满分 | 最低门槛 | 说明 |
|------|------|----------|------|
| root_cause_depth | 0.3 | ≥0.24 | 根因分析必须达到满分的 80% |
| solution_completeness | 0.3 | ≥0.24 | 方案完整性必须达到满分的 80% |
| code_quality | 0.2 | ≥0.16 | 代码质量必须达到满分的 80% |
| test_coverage | 0.2 | =0.20 | 测试覆盖率必须满分（100%） |

**通过条件**：全部维度达标，任意一项不达标则 ❌ REJECT。

### 功能/重构 Phase 4 tester E2E 验证

功能/重构任务在 Phase 4 完成后**必须**触发 tester E2E 验证：

```
Phase 4 完成 → 通知 tester 执行 E2E 验证
            → tester 回复 pass/fail
            → 收到 pass 后才能归档
```

### 归档前置条件

提示词在归档前必须验证（来自 `.claude/rules/05_task_convention.md`）：
1. Bug 修复：D3/D5/D6 reviewer 评分记录存在
2. 功能/重构：tester E2E 验证 pass 记录存在
3. 所有 Completion Criteria 已满足

**禁止将 🔶 前缀文件归档** — 🔶 表示部分完成，不得进入 archive 目录。

---

## 目的 / Purpose

自愈开发循环技能使系统能够自动检测开发问题、生成结构化的开发提示词、执行修复并更新项目任务管道。/ The Self Healing Dev Loop skill enables the system to automatically detect development issues, generate structured development prompts, execute fixes, and update project task pipelines.

此技能集成了以下子系统：/ This skill integrates the following subsystems:
- Dev Inspector / 开发检查器
- Auto Task Generator / 自动任务生成器
- RUNPROMPT / 运行提示词
- pipeline-dashboard / 流水线仪表盘

---

# 开发管道中的位置 / Position in Development Pipeline

此技能协调自动化开发工作流。

标准执行流程：

检测到运行时问题 / Runtime Issue Detected
↓
Dev Inspector 分析问题 / Dev Inspector analyzes problem
↓
Auto Task Generator 生成提示词 / Auto Task Generator generates prompt
↓
pipeline-dashboard 注册新任务 / pipeline-dashboard registers new task
↓
RUNPROMPT 执行提示词 / RUNPROMPT executes prompt
↓
执行器代理（Claude Code / Codex / Gemini）执行实现 / Executor agent performs implementation
↓
pipeline-dashboard 更新任务状态 / pipeline-dashboard updates task status

---

# 何时使用此技能 / When to Use This Skill

在以下情况下使用此技能：

- 检测到运行时错误 / a runtime error is detected
- 出现控制台错误 / a console error appears
- 在测试期间发现缺失功能 / a missing feature is discovered during testing
- 发现 UI 问题 / a UI issue is found
- 发生 API 失败 / an API failure occurs
- 出现工作流不一致 / a workflow inconsistency appears

---

# 技能组件 / Skill Components

此技能协调四个子系统。

## Dev Inspector

负责：

- 观察浏览器和运行时环境 / observing browser and runtime environment
- 分析控制台错误 / analyzing console errors
- 分析 API 失败 / analyzing API failures
- 识别可能的根本原因层 / identifying probable root cause layer

可能的层：前端 / 网络 / 后端 / 数据库

Dev Inspector 不修改代码，只执行诊断。

---

## Auto Task Generator

负责：

- 将检查的问题转换为结构化提示词 / converting inspected issues into structured prompts
- 分配提示词编号（从 `.sequence` 读取）/ assigning prompt numbers
- 选择正确的执行器代理（按 `.claude/rules/05_task_convention.md`）/ selecting the correct executor agent
- 生成符合项目规则的提示词 / generating prompts compliant with project rules

**任务类型按编号区间判断**（不按文件名片段）：

| 范围 / Range | 类别 / Category | 适用规则 |
|-------------|----------------|----------|
| 00001–09999 | 功能开发 / Feature Development | `01_workflow.md` (ADP) |
| 10101–19999 | Bug 修复 / Bug Fix | `02_debug.md` (8D) |
| 20101–29999 | 重构 / Refactoring | `01_workflow.md` (ADP) |
| 30101–39999 | 测试 / Testing | `01_workflow.md` (ADP) |

**执行器规则**（来自 `.claude/rules/05_task_convention.md`）：

| Executor | Scope |
|----------|-------|
| Claude Code | 简化任务、P0/P1 Bug、测试、重构 |
| Codex | 普通 Bug 修复、功能实现 |
| Gemini | 前端 UI 设计 |

---

## pipeline-dashboard 集成 / pipeline-dashboard Integration

每个生成的任务必须注册到 pipeline-dashboard。

必需的管道更新操作：

1. 注册新任务 / register new task
2. 分配执行器 / assign executor
3. 标记任务为待处理 / mark task as pending

---

## Lock 文件管理 / Lock File Management

**所有执行者（包括 Claude Code）必须创建 lock 文件。**

Lock 文件用于防止多 Agent 抢同一任务。创建规则：

| 场景 | 行为 |
|------|------|
| 任何执行者 | **创建 lock 文件**，交给目标执行器 |

Lock 文件命名：`promptsRec/active/<prompt_name>.lock`

Lock 文件内容应包含：

```
{
  "executor": "<executor_name>",
  "start_time": "<ISO timestamp>",
  "status": "running"
}
```

任务完成后删除 lock 文件以释放任务锁。

---

## RUNPROMPT 执行 / RUNPROMPT Execution

管道注册后，执行生成的提示词。

执行流程：

RUNPROMPT 从 promptsRec/active/ 读取提示词 / RUNPROMPT reads prompt from promptsRec/active/
↓
检查是否需要创建 lock 文件（所有执行者都需要） / Check if lock file needed
↓
分配的代理执行实现 / Assigned agent performs implementation
↓
删除 lock 文件 / Remove lock file
↓
生成执行报告 / Execution report generated
↓
提示词归档 / Prompt archived

---

# 根本原因分析规则 / Root Cause Analysis Rules

在生成任务之前，Dev Inspector 必须尝试根本原因分析。

可能的问题层包括：

- 前端层：Vue 运行时错误、错误的组件状态、错误的 API 调用
- 网络层：错误的基础 URL、缺少代理配置、请求头不匹配
- 后端层：缺少 API 路由、服务逻辑错误、未处理的异常
- 数据库层：架构不匹配、缺少表、SQL 查询错误

识别的层决定执行器。

---

# 提示词生成规则 / Prompt Generation Rules

生成的提示词必须遵循项目标准。

提示词头部格式：

Primary Executor / 主要执行者
Task Type / 任务类型
Stage / 阶段
Goal / 目标
Execution: RUNPROMPT

必需的提示词章节：

Required prompt sections:

Context / 上下文
Required References / 必需参考
Core Task / 核心任务
Required Work / 必需工作
Constraints / 约束条件
Completion Criteria / 完成标准

---

# 任务生命周期 / Task Lifecycle

每个任务必须遵循此生命周期：

已检测 / Detected
↓
已注册 (pipeline-dashboard) / Registered (pipeline-dashboard)
↓
待处理 / Pending
↓
RUNPROMPT 执行 / RUNPROMPT Execution
↓
已完成 / Completed

如果执行失败：

Status → 需要调查 / Investigation Required

---

# 安全约束 / Safety Constraints

此技能严禁：

- 直接修改生产数据 / modify production data directly
- 绕过 RUNPROMPT 执行 / bypass RUNPROMPT execution
- 不经检查生成提示词 / generate prompts without inspection
- 自动重新设计稳定架构 / redesign stable architecture automatically
- 假设数据库架构 / assume database schema

所有修复必须通过提示词执行。

---

# 完成标准 / Completion Criteria

当满足以下条件时，自愈开发循环被视为可运行：

1. 运行时问题触发 Dev Inspector / runtime issues trigger Dev Inspector
2. 任务自动生成 / tasks are generated automatically
3. pipeline-dashboard 注册任务 / pipeline-dashboard registers tasks
4. RUNPROMPT 执行任务 / RUNPROMPT executes tasks
5. pipeline-dashboard 更新任务状态 / pipeline-dashboard updates task status
6. 开发循环继续无需手动创建任务 / development loop continues without manual task creation
