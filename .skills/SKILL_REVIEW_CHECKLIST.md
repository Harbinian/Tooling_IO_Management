# 新技能接入审查清单 / New Skill Review Checklist

---

## 自动检查（CI 执行，G6 门禁）

- [ ] **G6-1** 文件体积 ≤ 20KB
- [ ] **G6-2** Frontmatter 包含所有必填字段（name, executor, auto_invoke, depends_on, triggers, rules_ref, version）
- [ ] **G6-2** `name` 与文件名一致（kebab-case）
- [ ] **G6-2** `executor` 为合法值（Claude Code / Codex / Human）
- [ ] **G6-2** `name` 与文件名匹配（去掉 .md 后缀）
- [ ] **G6-3** `triggers` 中的命令无重复（全局唯一）
- [ ] **G6-4** `depends_on` 中声明的技能文件均存在于 `.claude/skills/`
- [ ] **G6-5** 文件名前缀为 `skill-` 的元技能 `auto_invoke` 为 false

---

## 人工检查（H1 节点）

- [ ] 与现有技能无未声明的职责重叠（> 40%）
- [ ] 执行步骤的输出物定义清晰
- [ ] 完成标准可客观验证
- [ ] 双语结构完整（中文 + English）
- [ ] 体积 > 15KB 时已在 PR 中说明原因

---

## 审查流程

1. **提交前自检**：执行 `python scripts/check_skill_gates.py` 确认 G6 门禁全部通过
2. **PR 审查**：人工审查人工检查项
3. **合并后归档**：技能文件变更合并后自动归档

---

## G6 门禁说明

| 门禁 | 检查内容 | 不通过时 |
|------|---------|---------|
| G6-1 | 文件体积 ≤ 20KB | 阻断（>20KB）/ 警告（15-20KB） |
| G6-2 | Frontmatter 完整且合法 | 阻断 |
| G6-3 | 触发命令全局唯一 | 阻断 |
| G6-4 | depends_on 引用存在 | 阻断 |
| G6-5 | 元技能 auto_invoke 为 false | 阻断 |
