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
| D3 | 临时遏制措施 (Containment) | → 通知 `reviewer` 审核 |
| D4 | 根因分析 (5 Whys) | - |
| D5 | 永久对策 + 防退化宣誓 | → 通知 `reviewer` 审核 |
| D6 | 实施验证 (Implementation) | → 通知 `reviewer` 审核 |
| D7 | 预防复发 (Prevention) | - |
| D8 | 归档复盘 (Documentation) | - |

---

## 团队协作 / Team Protocol

**Reviewer Agent** 职责：
- 接收挂起通知，审查 D3/D5/D6 的输出
- 验证：根本原因是否充分、方案是否防退化、代码是否完整
- 回复 `approve` 或 `reject` + 反馈

**工作流**：
```
D3/D5/D6 完成 → SendMessage(to: "reviewer", type: "plan_approval_request")
              → reviewer 审核
              → 收到 approve 后继续
```

---

## 要求 / Requirements

每个 bug 修复必须包含：

- 根本原因解释 / root cause explanation
- 测试用例 / test case
- 回归预防 / regression prevention

**禁止使用临时补丁** / Temporary patches are forbidden.
