---
name: skill-audit-and-fix
executor: Claude Code
auto_invoke: false
depends_on: []
triggers:
  - /skill-audit
rules_ref:
  - .claude/rules/08_skill_convention.md
version: 1.0.0
---

# 技能审查与修复技能 / Skill Audit & Fix

---

## 目的 / Purpose

对 `.claude/skills/` 目录下所有技能文件执行结构审查并修复已知问题，同时生成可复用的技能审查框架，供后续新技能接入时使用。

本技能为元技能，用于维护技能文件本身的质量与规范。

---

## 上下文约束 / Context Constraints

- 规则来源：`.claude/rules/00_core.md` ~ `08_skill_convention.md`
- 技能目录：`.claude/skills/`
- 禁止修改生产代码
- 禁止在未声明 `executor` 的技能文件中添加自动执行逻辑
- 所有修改必须保持双语（中文 + English）结构
- **本技能为元技能**，不将自身列入审查范围

---

## 执行步骤 / Execution Steps

### Step 1｜体积扫描

```
执行以下检查，输出报告：
1. 列出所有技能文件及其字节数
2. 标记超过 15KB 的文件为 [OVERSIZE]
3. 标记低于 3KB 的文件为 [STUB?]
```

对每个 `[OVERSIZE]` 文件（> 20KB 阻断，15-20KB 警告）执行以下操作：

```
a. 识别可外部化的内容：
   - 硬编码的路径/URL 列表 → 提取到 docs/ 目录的 yaml 文件
   - 重复的流程描述 → 提取为共享 include 片段
   - 内联测试数据 → 提取到 tests/fixtures/

b. 重写技能文件，改为引用外部文件：
   ## 数据来源
   路径清单: docs/p0_paths.yaml

c. 目标：单个技能文件压缩至 15KB 以内
```

---

### Step 2｜Frontmatter 标准化

对每个缺少以下字段的技能文件，补全 frontmatter：

| 必填字段 | 说明 |
|---------|------|
| `name` | kebab-case，与文件名一致 |
| `executor` | Claude Code / Codex / Human |
| `auto_invoke` | 是否可被链式调用 |
| `depends_on` | 上游技能列表 |
| `triggers` | 触发命令列表 |
| `rules_ref` | 引用的规则文件 |
| `version` | 版本号 |

**Executor 判断标准**：

| 判断条件 | Executor 值 |
|---------|------------|
| 需要读写文件系统、执行命令 | `Claude Code` |
| 需要大规模代码生成/重构 | `Codex` |
| 需要人类判断业务语义 | `Human` |
| 仅生成文档/分析报告 | `Claude Code` |

---

### Step 3｜职责边界修复

对以下已知重叠技能对，在每个文件顶部添加边界声明区块：

#### 重叠对 A：`prompt-generator` vs `auto-task-generator`

在 `prompt-generator.md` 中添加：
```markdown
## 与相邻技能的边界
| 维度 | 本技能 | auto-task-generator |
|------|--------|-------------------|
| 输入 | 自由文本需求描述 | 结构化问题检测 |
| 输出 | 单个提示词文件 | 批量任务队列 |
| 使用场景 | 单次临时任务 | 系统性迭代开发 |
```

在 `auto-task-generator.md` 中添加对称声明。

#### 重叠对 B：`incident-capture` vs `incident-monitor`

| 维度 | 本技能 | 另一方 |
|------|--------|--------|
| 触发时机 | 被动接收，记录已发生事件 | 持续轮询，主动发现异常 |

#### 重叠对 C：`plan-to-prompt` vs `prompt-generator`

声明串行调用顺序：`requirement-harvest → plan-to-prompt → prompt-generator → auto-task-generator`

---

### Step 4｜调用关系声明

对以下已知隐式依赖，补全声明：

#### `self-healing-dev-loop.md`
```yaml
depends_on: [dev-inspector]
```

#### `scripted-e2e-builder.md`
```yaml
depends_on: [human-e2e-tester]
```

#### `release-precheck.md`
重写为 CI Gates 编排入口：
```markdown
## 执行内容
本技能不定义检查逻辑，仅按顺序编排以下门禁：
1. G3-1 单元测试覆盖率 ≥ 80%
2. G3-2 集成测试覆盖率 ≥ 60%
3. G3-3 前端单元测试
4. G3-4 E2E P0 路径覆盖
5. G5-3 归档前测试报告存在性
全部通过后输出 release-ready 标记，否则输出阻断报告。
规则来源：`.claude/rules/07_ci_gates.md`
```

---

### Step 5｜`codex-rectification-log.md` 重新定位

审查文件内容后执行判断：

```
IF 文件内容是运行时日志记录（包含具体错误记录）:
    → 移动到 docs/logs/ 目录
    → 在 skills/ 目录创建同名占位文件，内容为重定向说明

IF 文件内容是日志模板（包含占位符）:
    → 移动到 templates/ 目录
    → 文件名改为 codex-rectification-log.template.md

IF 文件内容是技能定义（包含执行逻辑）:
    → 补全 frontmatter（见 Step 2）
    → 添加边界声明说明与 bug-triage 的分工
```

---

## Phase 1 完成标准

输出 Phase 1 执行报告，包含：

```markdown
## Phase 1 执行报告

### 体积变化
| 文件 | 修改前 | 修改后 | 操作 |

### Frontmatter 补全情况
| 文件 | 补全字段 |

### 职责边界修复
| 重叠对 | 处理方式 |

### 调用关系声明
| 技能 | 新增依赖声明 |

### 未处理项（需人工判断）
- [ ] ...
```

---

## Phase 2 — 建立审查标准

Phase 1 完成后，生成以下文件：

### 输出文件 1：`.claude/skills/SKILL_STANDARD.md`

技能文件编写标准，内容包含：

```markdown
# 技能文件编写标准 / Skill File Standard

## 必须包含的结构
1. Frontmatter（name / executor / depends_on / triggers / rules_ref / version）
2. 目的 / Purpose（≤ 3 句话）
3. 上下文约束 / Context Constraints
4. 与相邻技能的边界声明（如有重叠技能）
5. 执行步骤（编号，每步有明确输出物）
6. 完成标准（可客观验证）

## 体积限制
- 单文件 ≤ 15KB
- 超出时必须外部化数据，不得压缩描述

## 禁止项
- 禁止硬编码路径（使用配置文件引用）
- 禁止内联大量测试数据
- 禁止隐式依赖（所有依赖必须在 depends_on 中声明）
- 禁止与现有技能职责重叠超过 40% 而不声明边界
```

### 输出文件 2：`.claude/skills/SKILL_REVIEW_CHECKLIST.md`

新技能接入时的审查清单：

```markdown
# 新技能接入审查清单 / New Skill Review Checklist

## 自动检查（CI 执行）
- [ ] 文件体积 ≤ 15KB
- [ ] Frontmatter 包含所有必填字段
- [ ] `name` 与文件名一致（kebab-case）
- [ ] `executor` 为合法值（Claude Code / Codex / Human）
- [ ] `depends_on` 中声明的技能文件均存在
- [ ] `triggers` 中的命令无重复（全局唯一）

## 人工检查（H1 节点）
- [ ] 与现有技能无未声明的职责重叠
- [ ] 执行步骤的输出物定义清晰
- [ ] 完成标准可客观验证
- [ ] 双语结构完整（中文 + English）
```

### 输出文件 3：`.claude/skills/SKILL_DEPENDENCY_MAP.md`

技能调用链路图（Mermaid），包含所有技能的 `depends_on` 关系。

---

## 完成标准 / Completion Criteria

技能完成当且仅当：

1. [ ] 所有技能文件体积 ≤ 20KB（G6-1）
2. [ ] 所有技能文件 Frontmatter 完整（G6-2）
3. [ ] 触发命令全局唯一（G6-3）
4. [ ] 所有 `depends_on` 引用存在（G6-4）
5. [ ] 所有元技能 `auto_invoke: false`（G6-5）
6. [ ] Phase 1 执行报告已输出
7. [ ] `SKILL_STANDARD.md` 已生成
8. [ ] `SKILL_REVIEW_CHECKLIST.md` 已生成
9. [ ] `SKILL_DEPENDENCY_MAP.md` 已生成
