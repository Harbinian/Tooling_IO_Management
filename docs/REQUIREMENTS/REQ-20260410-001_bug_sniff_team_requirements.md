# 需求：Bug 嗅探团队

## 基本信息 / Basic Information
- 需求编号：REQ-20260410-001
- 创建日期：2026-04-10
- 状态：已完善

## 5W2H 分析 / 5W2H Analysis

### What - 核心需求
**功能描述**：
建立一个 Bug 嗅探服务，通过技能触发（slash command）执行全量代码质量扫描，覆盖 G1-G6 CI 门禁规则，扫描完成后通过飞书 Webhook 推送报告，进程终止。

**输入**：
- 触发命令：`/bug-sniff`
- 飞书 Webhook URL：`https://open.feishu.cn/open-apis/bot/v2/hook/606947c1-f692-488f-b199-3848d15f577a`

**输出**：
- 飞书消息卡片，包含每个 gate 的 PASS/FAIL 状态
- FAIL 项包含文件路径和具体问题描述

---

### Why - 动机与价值
**业务背景**：
- 现有 CI/G1 hooks 仅在 `git commit` 时运行，无法发现两次 commit 之间积累的问题
- 代码审查报告 (`CODE_REVIEW_REPORT_20260409.md`) 显示仍有规则一致性问题未被 CI 捕获
- G1-2 pre-commit hook 存在 false positive bug（`[\u4e00-\u9fff]` 在 GNU grep 3.0 上被错误解析）

**预期价值**：
- 实现主动巡检，不等问题积累到 commit 才被发现
- 发现 G1-2 false positive 等 CI 规则本身的问题
- 减少代码入库前的规范性修复工作量

**成功标准**：
- 调用技能后全量扫描完成，报告发送至飞书
- 报告中每个 gate 有 PASS/FAIL 状态
- FAIL 项包含文件路径和具体问题描述
- 扫描过程只读，不修改任何文件

---

### Who - 角色与用户
**主要用户**：你（开发者）
**执行者**：Claude Code
**接收人**：你（飞书消息推送）

---

### When - 时间线
**触发方式**：手动技能触发，设计支持每小时调用
**使用频率**：手动触发（持续进行直到主动中止）

---

### Where - 使用场景
**使用环境**：开发环境 / 生产 CI 旁路
**集成需求**：飞书 Webhook（已有 URL，不依赖飞书其他 API）
**约束**：不修改代码库，只读扫描

---

### How - 实现方式
**建议实现方式**：
1. 新增 `bug-sniff` 技能（`.skills/bug-sniff/SKILL.md`）
2. 封装 G1-G6 扫描逻辑为独立可调用单元
3. 复用现有 `githooks/pre-commit` 中的检查逻辑
4. 扫描结果格式化后通过飞书 Webhook 发送

**参考系统**：
- 现有 `githooks/pre-commit` — G1 检查逻辑
- `docs/07_ci_gates.md` — G1-G6 门禁规则定义
- `utils/feishu_api.py` — 飞书 Webhook 发送

**技术栈**：Python + Feishu Webhook

---

### How Much - 资源与范围
**范围**：
- [x] G1-1 ~ G1-5 全部检查
- [x] G2-1 ~ G2-3 全部检查
- [x] G3-1 ~ G3-4 全部检查（G3 依赖 pytest/playwright，如未安装则 skip）
- [x] G4-1 ~ G4-2 全部检查
- [x] G5-1 ~ G5-3 全部检查
- [x] 飞书消息卡片推送
- [ ] G6 技能文件门禁（非代码质量，暂不包含）
- [ ] 自动修复功能（只报告，不修改）
- [ ] 报告持久化存储

**资源需求**：单个技能文件，预计 15KB 以内

---

## 验收标准 / Acceptance Criteria
1. 调用 `/bug-sniff` 技能后全量扫描完成，报告发送至飞书
2. 报告中每个 gate 有 PASS/FAIL 状态，FAIL 项包含文件路径和问题描述
3. 扫描过程只读，不修改任何文件
4. G1-2 检查使用 `grep -P` + `\p{Han}` 修复 false positive
5. G3 检查在依赖未安装时 skip，不阻断其他检查

## 关联文档 / Related Documents
- `docs/07_ci_gates.md` — CI 门禁规范
- `githooks/pre-commit` — 现有 G1 检查实现
- `utils/feishu_api.py` — 飞书 Webhook 发送
