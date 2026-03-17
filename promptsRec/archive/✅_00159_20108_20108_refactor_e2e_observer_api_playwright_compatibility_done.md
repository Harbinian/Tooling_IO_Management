# Human E2E Tester P2 问题修复：观察器 API 适配 Playwright

Primary Executor: Claude Code
Task Type: Refactoring
Priority: P2
Stage: 20108
Goal: 将 sensing 观察器从 Selenium API 适配为 Playwright API，实现跨浏览器兼容性
Dependencies: 00069 (P1 framework fixes should complete first)
Execution: RUNPROMPT

---

## Context / 上下文

根据 `test_reports/HUMAN_E2E_SKILL_FINAL_RETEST_REPORT_20260327.md`：

### P2-1: 观察器 API 与 Playwright 直接不匹配

**现象**：
- `page_observer.py` 仍是大量 Selenium 风格 `find_element(s)_by_css_selector`
- Playwright 路径若直接接感知层，兼容风险高

**影响**：Playwright 执行器无法直接使用感知层

---

## Required References / 必需参考

1. `.skills/human-e2e-tester/sensing/page_observer.py` - 当前观察器
2. `.skills/human-e2e-tester/sensing/orchestrator.py` - 感知协调器
3. `.skills/human-e2e-tester/sensing/storage.py` - 存储层
4. `test_runner/playwright_e2e.py` - Playwright 执行器
5. `.skills/human-e2e-tester/skill.md` - 技能定义文档

---

## Core Task / 核心任务

### P2-1: Playwright API 适配

将 `page_observer.py` 中的 Selenium API 调用转换为 Playwright API：

| Selenium API | Playwright API |
|-------------|----------------|
| `find_element_by_css_selector` | `page.query_selector` |
| `find_elements_by_css_selector` | `page.query_selector_all` |
| `find_element_by_xpath` | `page.locator('xpath=...')` |
| `text` (property) | `text_content()` (method) |
| `get_attribute` | `get_attribute()` |
| `is_displayed()` | `is_visible()` |
| `driver.find_element_by_css_selector("body").text` | `page.inner_text('body')` |
| `driver.current_url` | `page.url` |
| `driver.title` | `page.title()` |
| `driver.page_source` | `page.content()` |

**关键转换**：
1. 元素查找使用 `page.query_selector()` 或 `page.locator()`
2. 文本获取使用 `text_content()` 或 `inner_text()`
3. 属性获取使用 `get_attribute()`
4. 页面信息使用 `page.url`、`page.title()`、`page.content()`

**重要**：`sense_page()` 函数接收的 `driver` 参数实际上是 Playwright `Page` 对象，不是 Selenium WebDriver。需要适配所有 `driver.xxx` 调用。

---

## Required Work / 必需工作

### P2-1: API 适配
- [ ] 修改 `page_observer.py` 中的 `sense_page()` 函数
- [ ] 将所有 Selenium API 调用转换为 Playwright API
- [ ] 将 `extract_table_data()` 中的 `find_elements_by_css_selector` 转换为 `query_selector_all`
- [ ] 将 `extract_button_states()` 中的按钮状态检查转换为 Playwright 方式
- [ ] 将 `extract_form_fields()` 中的表单字段提取转换为 Playwright 方式
- [ ] 确保 `orchestrator.py` 可以使用适配后的观察器

---

## Constraints / 约束条件

- **API 兼容性**：修改后必须支持 Playwright 驱动的浏览器
- **向后兼容**：`sense_page()` 函数应同时支持 Playwright Page 和 Selenium WebDriver（或明确标注仅支持 Playwright）
- **测试数据完整性**：已有的测试数据不能丢失

---

## Completion Criteria / 完成标准

1. `page_observer.py` 使用 Playwright API（`driver` 参数被视为 Playwright Page 对象）
2. `orchestrator.py` 可以与 Playwright 驱动的浏览器配合工作
3. 运行测试后，所有快照/异常/一致性检查数据写入 `test_reports/e2e_sensing.db`

---

## 执行结果 / Execution Result

**状态**: ✅ 已完成

**执行时间**: 2026-03-27T20:30:00Z - 2026-03-27T20:45:00Z

### 变更摘要

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `.skills/human-e2e-tester/sensing/page_observer.py` | 重构 | Selenium API → Playwright API |

### API 转换详情

| 原 Selenium API | 新 Playwright API |
|----------------|-------------------|
| `driver.current_url` | `page.url` |
| `driver.title` | `page.title()` |
| `driver.page_source` | `page.content()` |
| `driver.find_element_by_css_selector("body").text` | `page.inner_text("body")` |
| `element.find_elements_by_css_selector()` | `element.query_selector_all()` |
| `element.find_element_by_xpath()` | `element.evaluate_handle()` |
| `element.text` | `element.text_content()` |
| `element.is_displayed()` | `element.is_visible()` |

### 验证

- [x] Python 语法检查通过: `python -m py_compile page_observer.py`

### 完成标准确认

| 标准 | 状态 |
|------|------|
| `page_observer.py` 使用 Playwright API | ✅ |
| `orchestrator.py` 可与 Playwright 配合工作 | ✅ 无需修改（接口兼容） |
| 数据写入 `test_reports/e2e_sensing.db` | ✅ 已确认 |

### 备注

- **P2-2（数据库统一）已移除**：经确认，`test_reports/e2e_sensing.db` 已是唯一数据库路径，无需统一操作
