# Bug Fix Prompt - 10191

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 10191
Goal: Fix wf_07 step in playwright_e2e.py - replace unstable Vue internal API with proper Element Plus UI interactions
Dependencies: None
Execution: RUNPROMPT

## Context / 上下文

E2E 测试在执行完整工作流时，wf_07 步骤（填写用途表单）失败。错误信息：
```
TypeError: Cannot read properties of undefined (reading 'exposed')
```

错误发生在 `test_runner/playwright_e2e.py` 第 634-666 行，代码尝试通过 Vue 内部 API 设置 el-select 值：
```javascript
page_taidongxu.evaluate("""
    () => {
        const vueApp = document.querySelector('#app').__vue_app__;
        if (vueApp) {
            const selects = document.querySelectorAll('.el-select');
            if (selects[0]) {
                selects[0].__vueParentComponent__.exposed.modelValue = '现场使用';
            }
        }
    }
""")
```

这是不稳定的实现方式，依赖于 Vue 内部结构，可能在不同版本中失效。

## Required References / 必需参考

- `test_runner/playwright_e2e.py` (lines 622-688) - 故障代码位置
- Element Plus Select component documentation
- Playwright documentation for interacting with el-select dropdowns

## D1 - 团队分工
- **Reviewer**: Claude Code (self-review)
- **Coder**: Claude Code
- **Architect**: Claude Code

## D2 - 问题描述 (5W2H)

| 要素 | 内容 |
|------|------|
| What | wf_07 步骤（填写用途/目标位置/计划使用时间）失败，JavaScript 错误 |
| Where | `test_runner/playwright_e2e.py` 第 634-666 行 |
| When | E2E 测试执行完整工作流时 |
| Who | 测试框架 (playwright_e2e.py) |
| Why | 使用了不稳定的 Vue 内部 API 进行表单填充 |
| How | 代码尝试通过 `__vueParentComponent__.exposed.modelValue` 设置 el-select 值 |
| How Many | 1 个测试步骤失败，导致完整工作流无法执行 |

## D3 - 临时遏制措施 (Containment)
**问题发现阶段，临时遏制：在测试代码中添加 try-catch，允许跳过失败的步骤继续执行后续测试**

当前 playwright_e2e.py 中的 wf_07 步骤已经包含 try-except，问题是表单填充方法本身需要修复。

**根本修复方案**：使用标准的 Playwright UI 交互替代 Vue 内部 API。

## D4 - 根因分析 (5 Whys)

#### 直接原因
代码使用 `document.querySelector('#app').__vue_app__` 获取 Vue 实例，然后通过 `__vueParentComponent__.exposed.modelValue` 设置 select 值。这些是 Vue 内部实现细节，在生产环境中不可靠。

#### 深层原因
Element Plus 的 el-select 组件不是通过原生 HTML select 实现的，而是使用自定义的 DOM 结构。开发者错误地认为可以通过 Vue 实例直接操作组件状态，而不是通过用户界面交互。

#### 全部问题点
1. 使用 `__vue_app__` 访问 Vue 实例 - 不稳定
2. 使用 `__vueParentComponent__` 访问组件 - 不稳定
3. 使用 `exposed.modelValue` 直接设置值 - 违反 Playwright 测试原则
4. 应该使用标准的用户交互：点击 select → 选择选项

## D5 - 永久对策 + 防退化宣誓

**永久对策**：
使用 Element Plus el-select 的标准 Playwright 交互方式：
1. 点击 el-select 触发下拉菜单
2. 等待 `.el-select-dropdown` 和 `.el-select-dropdown__item` 出现
3. 点击包含目标文本的选项 `.el-select-dropdown__item:has-text("现场使用")`

**防退化宣誓**：
我承诺修复后的代码：
- 不使用任何 Vue 内部 API（`__vue_app__`, `__vueParentComponent__`, `exposed` 等）
- 不使用 `document.querySelector` 获取 Vue 组件实例
- 仅使用 Playwright 标准 API 和 CSS/XPath 选择器进行 UI 交互
- 修复后运行 E2E 测试验证

## D6 - 实施验证 (Implementation)

需要修改的代码段：`test_runner/playwright_e2e.py` 第 622-688 行（wf_07 步骤）

**修改前**（错误）：
```python
page_taidongxu.evaluate("""
    () => {
        const vueApp = document.querySelector('#app').__vue_app__;
        if (vueApp) {
            const selects = document.querySelectorAll('.el-select');
            if (selects[0]) {
                selects[0].__vueParentComponent__.exposed.modelValue = '现场使用';
            }
        }
    }
""")
```

**修改后**（正确）：
```python
# 点击用途 select 并选择"现场使用"
page_taidongxu.click('.order-form .el-select >> nth=0', timeout=5000)
page_taidongxu.wait_for_selector('.el-select-dropdown__item:has-text("现场使用")', timeout=5000)
page_taidongxu.click('.el-select-dropdown__item:has-text("现场使用")', timeout=5000)

# 点击目标位置 select 并选择"A06"
page_taidongxu.click('.order-form .el-select >> nth=1', timeout=5000)
page_taidongxu.wait_for_selector('.el-select-dropdown__item:has-text("A06")', timeout=5000)
page_taidongxu.click('.el-select-dropdown__item:has-text("A06")', timeout=5000)
```

## D7 - 预防复发

#### 短期（立即生效）
- 更新测试代码规范，禁止使用 Vue 内部 API
- 在代码审查时检查是否有类似的 Vue API 调用

#### 长期（机制保证）
- 添加 ESLint/Prettier 规则检测 `__vue` 开头的属性访问
- 在 `.claude/rules/06_testing.md` 中添加测试代码规范章节

## D8 - 归档复盘

#### 经验教训
- 测试代码不应依赖框架内部实现
- Playwright 的核心理念是模拟真实用户交互
- UI 测试应通过可访问的 DOM 属性（class, id, text content）进行

#### 后续行动
- 修复后重新运行 E2E 测试验证
- 检查是否有其他类似的不稳定 API 调用

## Constraints / 约束条件

1. 不修改生产代码（仅修改测试代码）
2. 修复后代码必须使用 Playwright 标准 API
3. 修复后必须能够成功执行完整工作流测试
4. UTF-8 编码

## Completion Criteria / 完成标准

- [ ] 替换了所有 Vue 内部 API 调用为标准 Playwright UI 交互
- [ ] wf_07 步骤不再抛出 JavaScript 错误
- [ ] 表单字段（用途、目标位置）能够正确填充
- [ ] 完整工作流测试能够执行到获取订单号步骤
- [ ] 无引入新的错误
