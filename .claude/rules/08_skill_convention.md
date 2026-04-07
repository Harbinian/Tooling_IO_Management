# 技能约定规范 / Skill Convention

**规则编号**: 08
**适用范围**: `.claude/skills/` 目录下所有技能文件
**优先级**: 与 `00_core.md` 同级，技能相关决策以本文件为准

---

## 1. 文件结构规范 / File Structure

每个技能文件必须按以下顺序组织内容：

### 1.1 Frontmatter（必填）

```yaml
---
name: skill-name                  # kebab-case，必须与文件名一致
executor: Claude Code             # Claude Code | Codex | Human
auto_invoke: false                # 是否可被其他技能链式调用
depends_on: []                   # 上游技能列表，无则留空
triggers:                         # 触发命令，全局唯一
  - /skill-name
rules_ref:                        # 引用的规则文件
  - .claude/rules/00_core.md
version: 1.0.0
---
```

### 1.2 正文结构（必填区块，按顺序）

| 区块 | 说明 |
|------|------|
| `## 目的 / Purpose` | ≤ 3 句话，说明技能解决什么问题 |
| `## 上下文约束 / Context Constraints` | 权限边界、禁止操作、依赖环境 |
| `## 与相邻技能的边界` | 存在职责相近技能时必填，说明分工 |
| `## 执行步骤` | 编号步骤，每步有明确输出物 |
| `## 完成标准` | 可客观验证的交付物清单 |

---

## 2. 体积限制 / File Size Limits

| 状态 | 阈值 | 处理方式 |
|------|------|---------|
| 正常 | ≤ 15KB | 无需处理 |
| 警告 | 15KB ~ 20KB | 须在 PR 说明中解释原因，不阻断 |
| 阻断 | > 20KB | CI 拦截，必须外部化数据后方可合并 |

**外部化规则**：
- 路径/URL 列表 → `docs/` 目录 yaml 文件
- 角色权限矩阵 → `docs/rbac_matrix.yaml`
- 测试数据 → `tests/fixtures/`
- 重复流程片段 → 共享 include 文件

---

## 3. Executor 判断标准 / Executor Selection

| 判断条件 | Executor 值 |
|---------|------------|
| 需要读写文件系统、执行终端命令 | `Claude Code` |
| 需要大规模代码生成或重构 | `Codex` |
| 需要人类判断业务语义或做决策 | `Human` |
| 仅生成文档或分析报告 | `Claude Code` |

---

## 4. 依赖声明规则 / Dependency Declaration

- 所有上游技能必须在 `depends_on` 中显式声明
- 禁止隐式依赖（即技能执行时实际需要另一技能的输出，但未声明）
- `depends_on` 中引用的技能文件必须存在于 `.claude/skills/` 目录

---

## 5. 触发命令规则 / Trigger Command Rules

- 每个触发命令必须全局唯一，不得与其他技能重复
- 命令格式：`/kebab-case`，与 `name` 字段保持一致
- 元技能（管理其他技能的技能）命令前缀统一用 `/skill-`

---

## 6. 职责边界规则 / Responsibility Boundary

- 新技能与现有技能职责重叠超过 40% 时，必须在 `## 与相邻技能的边界` 区块中声明分工
- 重叠超过 60% 时，优先考虑合并而非新建
- 合并后的原文件保留，内容替换为重定向说明

---

## 7. 双语要求 / Bilingual Requirement

- 所有区块标题使用中英双语：`## 目的 / Purpose`
- 正文可选择主语言，但关键约束句必须双语
- Frontmatter 字段名使用英文

---

## 8. 元技能特殊规定 / Meta-Skill Special Rules

元技能（即管理、审查或生成其他技能的技能）须遵守：

- 不得将自身列入审查范围（禁止循环依赖）
- `auto_invoke` 必须为 `false`，只允许手动触发
- 必须在 `## 上下文约束` 中声明"本技能为元技能"

当前元技能清单：
- `skill-audit-and-fix.md`

---

## 9. 技能审查触发时机 / Skill Audit Triggers

以下情况需触发 `skill-audit-and-fix`：

| 触发条件 | 优先级 | 说明 |
|---------|--------|------|
| 新增技能文件 ≥ 3 个 | 中 | 批量接入后统一审查 |
| 任意技能文件体积超过 20KB | 高 | 立即处理 |
| 技能调用链路发生结构性变化 | 中 | 如新增主链路或废弃旧链路 |
| 规则文件 `00`~`08` 发生重大更新 | 低 | 确认技能与规则仍对齐 |
| 季度例行审查 | 低 | 每季度执行一次全量审查 |

> `skill-audit-and-fix` 是应急与维护工具，不属于日常开发流程，
> 不应在每次提交时触发。

---

## 10. 技能文件标准检查清单 / SKILL_FILE_CHECKLIST

### 自动检查（CI 执行，G6 门禁）

- [ ] 文件体积 ≤ 20KB（G6-1）
- [ ] Frontmatter 包含所有必填字段（name, executor, auto_invoke, depends_on, triggers, rules_ref, version）（G6-2）
- [ ] `name` 与文件名一致（kebab-case）（G6-2）
- [ ] `executor` 为合法值（Claude Code / Codex / Human）（G6-2）
- [ ] `depends_on` 中声明的技能文件均存在（G6-4）
- [ ] `triggers` 中的命令无重复（全局唯一）（G6-3）
- [ ] 元技能 `auto_invoke` 必须为 false（G6-5）

### 人工检查（H1 节点）

- [ ] 与现有技能无未声明的职责重叠（> 40%）
- [ ] 执行步骤的输出物定义清晰
- [ ] 完成标准可客观验证
- [ ] 双语结构完整（中文 + English）
- [ ] 体积 > 15KB 时已在 PR 中说明原因
