# 8D 问题解决协议 / 8D Problem Solving Protocol

仅用于调试或回归问题。

---

## 原则 / Principles

- **拒绝临时补丁**: 必须深挖根因，从代码、测试、流程三个维度预防复发
- **防退化红线**: 禁止"婴儿与洗澡水同倒"，必须死守旧有的核心业务边界
- **挂起节点**: D3、D5、D6 节点完成后必须通知 `reviewer` 审核，通过后才能继续

---

## 流程 / Steps

| 阶段 | 内容 | 审核 |
|------|------|------|
| D1 | 团队分工 (Reviewer, Coder, Architect) | - |
| D2 | 问题描述 (5W2H: What, Where, When, Who, Why, How) | - |
| D3 | 临时遏制措施 (Containment) | → **评分审核** |
| D4 | 根因分析 (5 Whys) | - |
| D5 | 永久对策 + 防退化宣誓 | → **评分审核** |
| D6 | 实施验证 (Implementation) | → **评分审核** |
| D7 | 预防复发 (Prevention) | - |
| D8 | 归档复盘 (Documentation) | - |

---

## 团队协作 / Team Protocol

**Reviewer Agent** 职责：
- 接收挂起通知，审查 D3/D5/D6 的输出
- 验证：根本原因是否充分、方案是否防退化、代码是否完整
- **使用评分制进行量化评估**，回复评分结果

**工作流**：
```
D3/D5/D6 完成 → SendMessage(to: "reviewer", type: "plan_approval_request")
              → reviewer 评分审核
              → 收到 ≥0.4 评分后继续
```

---

## 评分制审核 / Scoring Review

在 D3/D5/D6 节点，reviewer 必须使用评分制进行量化评估。

### 评估维度

| 维度 | 权重 | 评分标准 (0-1) |
|------|------|----------------|
| root_cause_depth | 0.3 | 根因分析是否穿透到真正原因（而非表面现象） |
| solution_completeness | 0.3 | 方案是否完整覆盖所有影响点 |
| code_quality | 0.2 | 代码是否符合项目规范（命名/编码/错误处理） |
| test_coverage | 0.2 | 是否有对应测试验证修复有效 |

### 评分输出模板

reviewer 必须输出以下格式：

```markdown
## 评分结果

| 维度 | 得分 | 理由 |
|------|------|------|
| root_cause_depth | 0.8 | 穿透到数据库连接池泄漏，而非仅修复表面错误 |
| solution_completeness | 0.7 | 覆盖了后端，前端异常处理遗漏 |
| code_quality | 0.9 | 符合项目编码规范 |
| test_coverage | 0.6 | 缺少异常场景测试 |

**加权总分**: 0.75/1.0

**结论**:
- ≥ 0.8 → ✅ APPROVE
- 0.4–0.8 → 🔶 APPROVE WITH SUGGESTIONS (附改进建议)
- < 0.4 → ❌ REJECT (必须重新做)
```

### 评分标准细则

**root_cause_depth**:
- 1.0: 找到真正根因，触及系统级问题
- 0.7-0.9: 找到直接原因，但未完全穿透
- 0.4-0.6: 只找到触发因素，未触及根本原因
- < 0.4: 仅处理了症状

**solution_completeness**:
- 1.0: 所有影响路径都有对应修复
- 0.7-0.9: 主要路径已覆盖，边界情况遗漏
- 0.4-0.6: 修复了部分问题，仍有遗漏
- < 0.4: 修复不完整或引入新问题

**code_quality**:
- 1.0: 符合所有项目规范，无警告
- 0.7-0.9: 有少量格式问题但不影响功能
- 0.4-0.6: 代码可工作但质量较差
- < 0.4: 代码质量差，难以维护

**test_coverage**:
- 1.0: 有完整单元测试 + 边界测试
- 0.7-0.9: 有主要路径测试，边界测试不足
- 0.4-0.6: 有简单测试，覆盖率不足
- < 0.4: 无测试或测试无效

---

## 要求 / Requirements

每个 bug 修复必须包含：

- 根本原因解释 / root cause explanation
- 测试用例 / test case
- 回归预防 / regression prevention

**禁止使用临时补丁** / Temporary patches are forbidden.
