# BUG 修复: Playwright选择器过时

## 任务编号
- **执行顺序号**: 00177
- **类型编号**: 10172
- **任务类型**: Bug修复任务 (10001-19999)
- **优先级**: P1

## 问题描述

### 症状
Playwright E2E测试中的以下步骤失败（选择器超时）：
```
❌ [taidongxu] wf_03: 选择出库类型 -> FAIL
   Page.click: Timeout 5000ms exceeded.
   Call log: waiting for locator("[value=\"outbound\"]")

❌ [taidongxu] wf_04: 打开工装搜索 -> FAIL
   Page.click: Timeout 5000ms exceeded.
   Call log: waiting for locator("button:has-text(\"搜索并添加工装\")")

❌ [taidongxu] wf_06: 选择工装 -> FAIL
   Page.click: Timeout 5000ms exceeded.
   Call log: waiting for locator(".el-table__row, [class*=\"tool-row\"], tr:first-child")

❌ [taidongxu] wf_08: 提交订单 -> FAIL
   未找到提交按钮
```

### 根本原因
`test_runner/playwright_e2e.py` 中使用的CSS选择器与当前前端UI不匹配。

## 前置依赖
- 无

## 修复方案

### 1. 调查当前前端UI结构

使用浏览器开发者工具检查：
- OrderCreate.vue 中"出库类型"单选按钮的实际选择器
- "搜索并添加工装"按钮的实际选择器
- 工装表格行的实际选择器
- 提交按钮的实际选择器

### 2. 更新playwright_e2e.py中的选择器

找到以下函数并更新选择器：
- `select_order_type_outbound()` - 选择出库类型
- `open_tool_search_dialog()` - 打开工装搜索
- `select_tool_from_table()` - 从表格选择工装
- `submit_order()` - 提交订单

### 3. 验证修复

运行一轮Playwright E2E测试：
```bash
cd E:/CA001/Tooling_IO_Management
python test_runner/playwright_e2e.py
```

确认以下步骤通过：
- wf_03: 选择出库类型 ✅
- wf_04: 打开工装搜索 ✅
- wf_06: 选择工装 ✅
- wf_08: 提交订单 ✅

## 约束条件
- 只修改 `test_runner/playwright_e2e.py`
- 不修改前端代码
- 保持测试逻辑不变，只更新选择器

## 完成标准
1. wf_03, wf_04, wf_06, wf_08 全部通过
2. 工作流能够完整执行到最后一步

## 报告输出
写入 `test_reports/BUGFIX_10172_PLAYWRIGHT_SELECTORS_REPORT_YYYYMMDD.md`
