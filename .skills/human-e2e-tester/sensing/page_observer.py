# -*- coding: utf-8 -*-
"""
PageContextObserver - 页面感知层 (Playwright 版本)

读取当前页面 DOM 状态，感知元素存在性、文本内容、数值、状态标签。
输出 PageSnapshot。

支持 Playwright Page 对象。
"""

from typing import Optional, Any, Union
from .snapshot import (
    PageSnapshot,
    STATUS_LABEL_MAP,
    LABEL_TO_STATUS,
    GIBBERISH_PATTERNS,
    TestContext,
)

# Playwright 或 Selenium WebDriver 的类型别名
PageLike = Any


def detect_page_type(url: str, page_title: str = "") -> str:
    """
    根据 URL 和页面标题判断页面类型

    Args:
        url: 当前 URL
        page_title: 页面标题（可选）

    Returns:
        页面类型: "OrderList", "OrderDetail", "OrderCreate", "KeeperProcess",
                 "Dashboard", "Settings", "Login", "Unknown"
    """
    url_lower = url.lower()

    if "/login" in url_lower or "登录" in page_title:
        return "Login"
    elif "/create" in url_lower or "/new" in url_lower:
        return "OrderCreate"
    elif "/detail" in url_lower or "/order/" in url_lower:
        return "OrderDetail"
    elif "/keeper" in url_lower or "保管员" in page_title:
        return "KeeperProcess"
    elif "/dashboard" in url_lower or "/home" in url_lower or "首页" in page_title:
        return "Dashboard"
    elif "/settings" in url_lower or "设置" in page_title:
        return "Settings"
    elif "/tool-io" in url_lower or "出入库" in page_title:
        return "OrderList"

    return "Unknown"


def extract_order_no_from_url(url: str) -> Optional[str]:
    """从 URL 中提取订单号"""
    import re
    # 匹配常见的订单号格式
    patterns = [
        r'/order/([A-Z0-9]{10,})',
        r'/detail/([A-Z0-9]{10,})',
        r'order_no=([A-Z0-9]{10,})',
        r'([A-Z]{2,}\d{8,})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_status_label(text_content: str, html_content: str = "") -> Optional[str]:
    """
    从页面内容中提取订单状态标签

    状态标签的特征：
    - 在 Element Plus 的 el-tag 组件中
    - 通常带有颜色类名 (success/warning/danger/info)
    - 文本是 STATUS_LABEL_MAP 中的值之一
    """
    for label in STATUS_LABEL_MAP.values():
        if label in text_content:
            return label
    return None


def detect_gibberish_text(text: str) -> bool:
    """
    检测是否有乱码文本

    Args:
        text: 待检测的文本

    Returns:
        True 如果发现乱码特征字符
    """
    for pattern in GIBBERISH_PATTERNS:
        if pattern in text:
            return True
    return False


def count_visible_elements(elements: list) -> int:
    """计算可见元素的数量"""
    count = 0
    for el in elements:
        try:
            if el.is_visible():
                count += 1
        except Exception:
            pass
    return count


def extract_table_data(page, selector: str) -> tuple[int, list[dict]]:
    """
    从表格元素中提取数据 (Playwright 版本)

    Args:
        page: Playwright Page 对象
        selector: 表格选择器

    Returns:
        (行数, 行数据列表)
    """
    rows = []
    try:
        # 获取表头
        headers = []
        header_cells = page.query_selector_all(f"{selector} thead th") or \
                       page.query_selector_all(f"{selector} .el-table__header th")
        for cell in header_cells:
            headers.append(cell.text_content().strip() if cell else "")

        # 获取数据行
        body_rows = page.query_selector_all(f"{selector} tbody tr") or \
                    page.query_selector_all(f"{selector} .el-table__body tr")

        for row in body_rows:
            cells = row.query_selector_all("td")
            row_data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    row_data[headers[i]] = (cell.text_content() or "").strip()
                else:
                    row_data[f"col_{i}"] = (cell.text_content() or "").strip()
            if row_data:
                rows.append(row_data)
    except Exception:
        pass

    return len(rows), rows


def extract_button_states(page, selector: str) -> tuple[list[str], list[str]]:
    """
    提取按钮状态 (Playwright 版本)

    Args:
        page: Playwright Page 对象
        selector: 按钮容器选择器

    Returns:
        (可见且可点击的按钮列表, 禁用/灰掉的按钮列表)
    """
    visible = []
    disabled = []

    try:
        container = page.query_selector(selector)
        if not container:
            return visible, disabled

        buttons = container.query_selector_all("button") or \
                  container.query_selector_all(".el-button")

        for btn in buttons:
            btn_text = (btn.text_content() or "").strip()
            if not btn_text:
                # 尝试从 aria-label 或 title 获取
                btn_text = btn.get_attribute("aria-label") or btn.get_attribute("title") or "unnamed"

            try:
                is_disabled = btn.get_attribute("disabled") is not None
                is_visible = btn.is_visible()

                if not is_visible:
                    continue

                if is_disabled:
                    disabled.append(btn_text)
                else:
                    visible.append(btn_text)
            except Exception:
                pass
    except Exception:
        pass

    return visible, disabled


def extract_form_fields(page, selector: str) -> dict[str, Any]:
    """
    从表单中提取字段名和值 (Playwright 版本)

    Args:
        page: Playwright Page 对象
        selector: 表单选择器

    Returns:
        字段名字典
    """
    fields = {}

    try:
        form = page.query_selector(selector)
        if not form:
            return fields

        # 提取输入框
        inputs = form.query_selector_all(
            "input:not([type='hidden']), textarea, .el-input__inner, .el-textarea__inner"
        )
        for inp in inputs:
            try:
                # 尝试通过 XPath 查找前面的 label
                label_el = inp.evaluate_handle(
                    "el => el.closest('.el-form-item')?.querySelector('label')"
                )
                if label_el:
                    label_text = (label_el.text_content() or "").strip().rstrip(":")
                else:
                    label_text = "unknown"

                # 获取输入框的值
                value = inp.input_value() if hasattr(inp, 'input_value') else (inp.text_content() or "")
                if not value:
                    value = inp.get_attribute("value") or ""
                fields[label_text] = value
            except Exception:
                pass

        # 提取选择框
        selects = form.query_selector_all(".el-select, select")
        for sel in selects:
            try:
                # 查找 label
                label_el = sel.evaluate_handle(
                    "el => el.closest('.el-form-item')?.querySelector('label')"
                )
                if label_el:
                    label_text = (label_el.text_content() or "").strip().rstrip(":")
                else:
                    label_text = "unknown"

                # 获取选中的值
                selected_option = sel.query_selector(
                    ".el-input__inner, .el-select__wrapper, select option:checked"
                )
                value = (selected_option.text_content() or "").strip() if selected_option else ""
                fields[label_text] = value
            except Exception:
                pass
    except Exception:
        pass

    return fields


def capture_error_message(page_source: str, visible_text: str) -> Optional[str]:
    """
    捕获页面上的错误消息

    错误消息的特征：
    - Element Plus 的 el-alert、el-message、el-message-box-error
    - class 包含 "error"、"danger"、"is-error"
    - aria-live="assertive" 的元素
    """
    import re

    # 匹配 Element Plus 错误消息
    patterns = [
        r'<el-alert[^>]*type="error"[^>]*>.*?<span[^>]*>(.*?)</span>',
        r'<div[^>]*class="[^"]*el-message[^"]*[^"]*error[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*is-error[^"]*"[^>]*>(.*?)</div>',
        r'class="el-alert__title">(.*?)</span>',
        r'aria-live="assertive"[^>]*>(.*?)</div>',
    ]

    for pattern in patterns:
        match = re.search(pattern, page_source, re.DOTALL)
        if match:
            return match.group(1).strip()

    # 从可见文本中查找
    error_keywords = ["错误", "失败", "异常", "不能", "无法", "失败", "invalid", "error", "failed"]
    lines = visible_text.split("\n")
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in error_keywords):
            if len(line) < 200:  # 错误消息通常较短
                return line.strip()

    return None


def sense_page(
    page: PageLike,
    context: Optional[TestContext] = None
) -> PageSnapshot:
    """
    感知当前页面，生成页面快照 (Playwright 版本)

    这是 PageContextObserver 的核心函数，模拟真人"看"页面的方式。

    Args:
        page: Playwright Page 对象
        context: 测试上下文（可选）

    Returns:
        PageSnapshot: 页面快照对象
    """
    try:
        url = page.url
    except Exception:
        url = ""

    try:
        page_title = page.title()
    except Exception:
        page_title = ""

    try:
        page_source = page.content()
    except Exception:
        page_source = ""

    try:
        visible_text = page.inner_text("body")
    except Exception:
        visible_text = ""

    # 检测页面类型
    page_name = detect_page_type(url, page_title)

    # 提取订单号
    order_no = extract_order_no_from_url(url)

    # 提取状态标签
    order_status = extract_status_label(visible_text, page_source)

    # 检测乱码
    has_gibberish = detect_gibberish_text(visible_text + page_source)

    # 基础快照
    snapshot = PageSnapshot(
        page_name=page_name,
        url=url,
        order_no=order_no,
        order_status=order_status,
        raw_text=visible_text,
        raw_html=page_source,
    )

    # 根据页面类型进行专门感知
    if page_name == "OrderList":
        _sense_order_list_page(page, snapshot)
    elif page_name == "OrderDetail":
        _sense_order_detail_page(page, snapshot)
    elif page_name == "OrderCreate":
        _sense_order_create_page(page, snapshot)

    # 捕获错误消息
    snapshot.error_message = capture_error_message(page_source, visible_text)

    # 检测乱码
    if has_gibberish:
        snapshot.warning_message = "页面存在乱码文本"

    # 更新上下文
    if context:
        context.current_order_no = order_no
        if order_status:
            context.current_order_status = LABEL_TO_STATUS.get(order_status)

    return snapshot


def _sense_order_list_page(page, snapshot: PageSnapshot):
    """感知订单列表页面 (Playwright 版本)"""
    try:
        # 查找表格
        table = page.query_selector(".el-table, table")
        if table:
            rows, table_data = extract_table_data(page, ".el-table, table")
            snapshot.table_rows = rows
            snapshot.table_data = table_data

            # 提取第一行的关键信息（如果有数据）
            if table_data:
                first_row = table_data[0]
                snapshot.fields = first_row

                # 尝试提取订单号和状态
                for key, value in first_row.items():
                    if "单号" in key or "单据号" in key:
                        snapshot.order_no = value
                    if "状态" in key:
                        snapshot.order_status = value

        # 查找按钮
        try:
            visible, disabled = extract_button_states(page, ".el-table, table")
            snapshot.visible_buttons = visible
            snapshot.disabled_buttons = disabled
        except Exception:
            pass

    except Exception:
        pass


def _sense_order_detail_page(page, snapshot: PageSnapshot):
    """感知订单详情页面 (Playwright 版本)"""
    try:
        # 查找概览信息区域
        overview_selectors = [
            ".order-overview",
            ".detail-card",
            "[class*='overview']",
            "[class*='detail']",
        ]

        for selector in overview_selectors:
            try:
                overview = page.query_selector(selector)
                if overview:
                    snapshot.fields = extract_form_fields(page, selector)
                    break
            except Exception:
                continue

        # 查找状态标签
        try:
            status_tag = page.query_selector(".el-tag, [class*='status'], [class*='badge']")
            if status_tag:
                snapshot.order_status = (status_tag.text_content() or "").strip()
        except Exception:
            pass

        # 查找工装明细表格
        try:
            item_table = page.query_selector(".items-table, .tool-table, [class*='item'] table")
            if item_table:
                rows, items = extract_table_data(page, ".items-table, .tool-table, [class*='item'] table")
                snapshot.items_count = rows
                snapshot.table_data = items
        except Exception:
            pass

        # 查找驳回原因
        try:
            reject_area = page.query_selector("[class*='reject'], [class*='reason'], .rejection-reason")
            if reject_area:
                snapshot.reject_reason = (reject_area.text_content() or "").strip()
        except Exception:
            pass

        # 查找操作按钮
        try:
            visible, disabled = extract_button_states(page, ".action-buttons, .detail-actions, [class*='action']")
            snapshot.visible_buttons = visible
            snapshot.disabled_buttons = disabled
        except Exception:
            pass

    except Exception:
        pass


def _sense_order_create_page(page, snapshot: PageSnapshot):
    """感知订单创建页面 (Playwright 版本)"""
    try:
        # 查找已选工装表格
        try:
            selected_table = page.query_selector(".selected-tools, .tool-list, [class*='selected'] table")
            if selected_table:
                rows, items = extract_table_data(page, ".selected-tools, .tool-list, [class*='selected'] table")
                snapshot.items_count = rows
                snapshot.table_data = items
        except Exception:
            pass

        # tool_count is now derived from items_count (which comes from table rows)
        # tool_count represents the actual items.length, not a deprecated static field
        if snapshot.items_count is not None:
            snapshot.tool_count = snapshot.items_count

        # 查找表单
        try:
            form = page.query_selector("form, .order-form")
            if form:
                snapshot.fields = extract_form_fields(page, "form, .order-form")
        except Exception:
            pass

    except Exception:
        pass
