# playwright_e2e.py 脚本选择器过时修复

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P2
Stage: 10169
Goal: 修复 playwright_e2e.py 中过时的 UI 选择器，确保 E2E 测试可正常运行
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

在 Human E2E 测试执行中，`playwright_e2e.py` 脚本存在多个选择器过时问题：

### 问题 1: 登录按钮文本

**实际 UI 文本**: "进入系统"
**脚本使用**: "登录"

```python
# 错误代码
page.click('button[type="submit"]', timeout=5000)  # 按钮文本是"进入系统"
```

### 问题 2: 登录检测逻辑

**问题**: 登录后立即检查 URL 变化，但可能需要等待重定向完成
**当前代码**:
```python
page.click('button[type="submit"]', timeout=5000)
page.wait_for_load_state('networkidle', timeout=10000)
if "/login" not in page.url:
    print("✅ 登录成功")
```

### 问题 3: 其他选择器

根据实际页面检查：
- 工装搜索对话框的触发按钮
- 出库/入库类型选择器
- 提交/确认按钮文本

---

## Required References / 必需参考

1. `test_runner/playwright_e2e.py` - 需要修复的脚本
2. `frontend/src/pages/auth/LoginPage.vue` - 登录页面（检查实际按钮文本）
3. `frontend/src/pages/tool-io/OrderCreate.vue` - 创建订单页面
4. `frontend/src/pages/tool-io/OrderList.vue` - 订单列表页面

---

## Core Task / 核心任务

### 诊断阶段

使用 Playwright 检查实际页面元素：

1. **登录页**：
   - 按钮文本应该是 `进入系统`
   - input[type="text"] placeholder 是 `请输入用户名`
   - input[type="password"] placeholder 是 `请输入密码`

2. **创建订单页**：
   - 订单类型选择（出库/入库）
   - 工装搜索触发按钮
   - 提交按钮

3. **订单详情页**：
   - 确认按钮
   - 取消按钮
   - 通知按钮

### 修复阶段

1. **修复登录函数**：
   ```python
   def login(page: Page, username: str, password: str) -> bool:
       page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
       page.fill('input[type="text"]', username)
       page.fill('input[type="password"]', password)
       page.click('button:has-text("进入系统")')  # 修复按钮文本
       page.wait_for_timeout(2000)  # 等待重定向
       page.wait_for_load_state('networkidle', timeout=10000)
       return "/login" not in page.url
   ```

2. **修复所有页面选择器**：确保与实际 UI 匹配

### 验证阶段

运行 `python test_runner/playwright_e2e.py` 验证：
- 快速冒烟测试应通过
- 登录不应失败

---

## Required Work / 必需工作

- [ ] Step 1: 检查 LoginPage.vue 获取实际按钮文本和 input 选择器
- [ ] Step 2: 修复 login() 函数
- [ ] Step 3: 检查 OrderCreate.vue 获取创建订单页面选择器
- [ ] Step 4: 修复工作流测试中的选择器
- [ ] Step 5: 运行测试验证修复

---

## Constraints / 约束条件

- **不改变测试逻辑**：只修复选择器，不改变测试步骤
- **使用 text-content 选择器**：`button:has-text()` 比精确文本匹配更健壮
- **添加合理等待**：使用 `wait_for_timeout` 而非硬编码 sleep

---

## Completion Criteria / 完成标准

1. 登录步骤不再报告 "登录失败 - URL 未变化"
2. 快速冒烟测试可以通过（登录 -> 首页 -> 订单列表 -> 创建页）
3. 完整工作流测试能够创建并提交订单
4. 所有 click/text_content 选择器与实际 UI 匹配
