Primary Executor: Claude Code
Task Type: 技术架构升级
Stage: 025
Goal: 升级现有 pipeline-dashboard Skill，使其支持任务调度、依赖关系管理和优先级判断，同时保持现有扫描和推荐功能。
Execution: RUNPROMPT

---

# Context

当前 pipeline-dashboard 仅支持扫描 promptsRec 目录、分类任务状态（Pending、Running、Completed）并推荐下一个任务。  

现有问题与改进目标：

1. 无任务优先级判断  
2. 无依赖关系检查（前端任务依赖后台完成等）  
3. 无智能调度逻辑  
4. 不区分 Bug 优先级与 Feature 顺序执行  

本任务旨在：

- 在现有 Skill 基础上升级
- 保留文件扫描、任务状态分类和推荐功能
- 添加调度模块、依赖检测和任务优先级规则
- 输出规范中文提示词供 RUNPROMPT 执行
- 保持与 RUNPROMPT、Codex/Gemini/Claude Code 执行流程兼容

---

# Required References

- 当前 pipeline-dashboard Skill 源码  
- promptsRec/ 文件规范  
- 项目现有任务类型规则（Bug 100–199, Feature 000–099）  
- RUNPROMPT 执行流程  

---

# Core Task

升级 pipeline-dashboard Skill，实现以下功能：

1. **任务优先级判断**
   - Bug 提示词优先级最高
   - Feature 按编号顺序执行
   - 前端任务依赖后端完成
   - 同类任务按先来先执行原则

2. **依赖关系检测**
   - 前端页面迁移必须等待对应后端逻辑完成
   - Keeper UI 页面必须等待 Keeper 后端流程完成
   - 结构化消息/通知记录 UI 等必须等待业务逻辑完成

3. **推荐任务输出**
   - 输出下一个推荐任务
   - 显示文件名、执行模型、依赖状态
   - 显示 Pending、Running、Completed 数量

4. **集成现有功能**
   - 保留扫描 promptsRec/ 目录
   - 保留状态分类逻辑
   - 保留报告生成逻辑

---

# Required Work

- 在 pipeline-dashboard Skill 源码中新增 Scheduler 模块  
- 通过分析 prompt 文件名与内容推断依赖关系  
- 实现任务优先级排序逻辑  
- 输出推荐任务时附加依赖信息  
- 保留对 `.lock` 文件的检查  
- 保证 dashboard 不直接执行任务，仅推荐  

---

# Constraints

- 不得修改 RUNPROMPT 执行逻辑  
- 不得直接执行任务  
- 不得假定数据库或前端状态  
- 升级后 Skill 必须兼容现有 pipeline-dashboard 输出格式  
- 必须遵守项目提示词编号和分类规则  

---

# Completion Criteria

升级完成后，Skill 应满足：

1. 扫描 promptsRec 正确分类任务状态  
2. 能识别 Bug 和 Feature 优先级  
3. 能检测依赖关系并推荐合法顺序  
4. 输出推荐任务报告包含：
   - 文件名
   - 执行模型
   - 依赖状态
   - 当前状态统计  
5. 保持与 RUNPROMPT 流程兼容