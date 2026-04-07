# 热修复 SOP / HOTFIX SOP

---

## 与 8D 协议的关系 / Relationship with 8D Protocol

HOTFIX 是 8D 的**紧急快速通道**，适用于生产环境紧急问题。

| 对比项 | HOTFIX | 8D |
|--------|--------|----|
| 适用场景 | 生产紧急，需立即止血 | 非紧急 Bug，需根因分析 |
| 流程长度 | 5步（简化） | 8步（完整） |
| 审核节点 | tester 冒烟测试 | reviewer 评分 × 3 |
| 事后要求 | 必须在 3 个工作日内补全 8D D4-D8 | 完整执行 |

> ⚠️ 若 HOTFIX 完成后未在 3 个工作日内补全 8D，禁止归档。

---

## 红线（必须遵守）/ RED LINES

1. **单步执行锁**: 禁止并行，一次只执行一个原子变更
2. **强制挂起**: 每步完成后必须通知 `tester` 冒烟测试，通过后才能继续
3. **零假设验证**: 见 `00_core.md` — Zero-Assumption Policy。
4. **UTF-8 铁律**: 见 `00_core.md` — 编码章节，所有文件操作必须遵守。
5. **I/O 节流**: 批量文件读取每次 ≤10 个，防止缓冲区溢出

---

## 流程 / Steps

| 步骤 | 内容 | 审核 |
|------|------|------|
| 1 | 识别受影响模块 | - |
| 2 | 创建 RFC 文档（含爆炸半径评估） | Review |
| 3 | 分步执行 + 冒烟测试 | → 通知 `tester` |
| 4 | 回滚预案（如失败） | - |
| 5 | 归档 | - |

---

## 团队协作 / Team Protocol

**Tester Agent** 职责：
- 接收冒烟测试请求
- 执行 Dry Run 验证变更正确性
- 回复 `pass` 或 `fail` + 原因

**工作流**：
```
每步代码变更完成 → SendMessage(to: "tester", 冒烟测试请求)
               → tester 执行验证
               → 收到 pass 后继续下一步
```

---

## RFC 格式 / RFC Template

```markdown
# 变更: [简述问题]

## 爆炸半径
- 影响范围: [文件/模块]
- 潜在风险: [风险点]

## 执行步骤
- [ ] Step 1: [具体操作]
- [ ] Step 2: [具体操作]

## 回滚方案
如失败，执行的回滚命令: git checkout <file>
```

---

## 原则 / Principles

1. **最小影响范围** / Minimal blast radius
2. **原子性变更** / Atomic changes
3. **立即验证** / Immediate verification
