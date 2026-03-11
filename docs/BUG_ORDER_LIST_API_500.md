# Bug 订单列表 API 500 / Bug Order List API 500

---

## 观察到的现象 / Observed Symptom

待处理的 bug 报告描述了在以下端点上的 `500 Internal Server Error`: / The pending bug report described a `500 Internal Server Error` on:

- `GET /api/tool-io-orders`

这阻止了订单列表页面通过后端 API 加载订单数据。 / This prevented the order list page from loading order data through the backend API.

---

## 根本原因 / Root Cause

`database.py` 中的订单列表查询构建器使用了遗留的 `TOP ... NOT IN (SELECT TOP ...)` 分页查询，该查询重复了相同的过滤 `WHERE` 子句两次: / The order list query builder in `database.py` used a legacy `TOP ... NOT IN (SELECT TOP ...)` pagination query that repeated the same filtered `WHERE` clause twice:

- 一次在外层查询中 / once in the outer query
- 一次在子查询中 / once in the subquery

然而，代码只将过滤参数元组传递给 `execute_query(...)` 一次。 / However, the code only passed the filter parameter tuple once to `execute_query(...)`.

这意味着任何使用可选过滤的请求，如: / That meant any request using optional filters such as:

- `order_status` / 订单状态
- `keyword` / 关键词
- `initiator_id` / 发起人ID
- `keeper_id` / 保管员ID

可能因 SQL 参数数量不匹配而失败并返回 `500`。 / could fail with a SQL parameter-count mismatch and return `500`.

在当前环境中，无过滤的基本路由仍返回 `200`，因此这是订单列表端点中的潜在后端 bug，而非路由注册失败。 / The unfiltered base route was still returning `200` in the current environment, so this was a latent backend bug in the order list endpoint rather than a route registration failure.

---

## 修改的文件 / Files Changed

- `database.py`
- `tests/test_get_tool_io_orders.py`

---

## 应用的修复 / Fix Applied

`get_tool_io_orders(...)` 现在使用单个分页 SQL 查询: / `get_tool_io_orders(...)` now uses a single paginated SQL query:

- `SELECT ... WHERE ... ORDER BY ... OFFSET ... FETCH NEXT ...`

这使占位符计数与提供的参数元组保持一致，并保留现有的 JSON 响应结构。 / This keeps the placeholder count aligned with the provided parameter tuple and preserves the existing JSON response structure.

---

## 验证结果 / Verification Results

于 2026 年 3 月 12 日验证: / Verified on March 12, 2026:

- Flask 路由 `GET /api/tool-io-orders?page_no=1&page_size=20` 返回 `200` / Flask route `GET /api/tool-io-orders?page_no=1&page_size=20` returned `200`
- Flask 路由 `GET /api/tool-io-orders?order_status=submitted&keyword=P-001&page_no=1&page_size=20` 返回 `200` / Flask route `GET /api/tool-io-orders?order_status=submitted&keyword=P-001&page_no=1&page_size=20` returned `200`
- API 响应是包含列表数据和分页字段的有效 JSON / API responses were valid JSON with list data and pagination fields
- `GET /api/tools/search?page_no=1&page_size=1` 返回 `200` 且 `success: true` / `GET /api/tools/search?page_no=1&page_size=1` returned `200` with `success: true`
- `python -m pytest tests/test_get_tool_io_orders.py` 通过 / `python -m pytest tests/test_get_tool_io_orders.py` passed
- `python -m py_compile web_server.py database.py backend/services/tool_io_service.py` 通过 / `python -m py_compile web_server.py database.py backend/services/tool_io_service.py` passed
- `frontend/` 中的 `npm run build` 通过 / `npm run build` in `frontend/` passed

---

## 剩余风险 / Remaining Risks

- 在此任务中，我没有对实时订单列表页面运行端到端浏览器交互; 前端验证仅限于构建成功加上后端 API 确认。/ I did not run an end-to-end browser interaction against the live order list page in this task; frontend verification was limited to build success plus backend API confirmation.
- 我没有执行写入路径的订单提交流，因为这会改变活动数据库状态。/ I did not execute write-path order submission flows because that would mutate the active database state.
---

## 瀛愰棶棰? / Sub-Issues

### Sub-Issue 1

- Pagination placeholder mismatch in `database.py`
- Failure layer: database query / pagination logic
- Status: fixed in the previous Bug 103 repair pass

### Sub-Issue 2

- Follow-up verification requested on March 12, 2026
- Confirmed request path: `GET /api/tool-io-orders`
- Expected evidence: fresh backend traceback for a continuing `500`
- Actual evidence: no traceback reproduced in the current workspace state
- Confirmed layers checked: route handler, request parsing, service layer, database query, pagination logic, response serialization
- Conclusion: the previously fixed Bug 103 issue is not currently reproducing a new backend `500`

---

## Follow-up Verification / 鍚庣画楠岃瘉

Verified on March 12, 2026 for the follow-up prompt:

- `GET /api/tool-io-orders` returned `200`
- `GET /api/tool-io-orders?order_status=submitted&keyword=P-001&page_no=1&page_size=20` returned `200`
- `GET /api/tool-io-orders?date_from=2026-03-11&date_to=2026-03-12&page_no=1&page_size=20` returned `200`
- No backend traceback was produced for these requests
- Current follow-up outcome: backend API is healthy for the verified order-list scenarios, but manual UI confirmation is still recommended before changing the archive confirmation status
---

## Frontend Error Evidence / 鍓嶇閿欒璇佹嵁

```text
client:789 [vite] connecting...
:5173/api/tool-io-orders?keyword=&order_type=&order_status=&initiator_id=&keeper_id=&page_no=1&page_size=20:1   Failed to load resource: the server responded with a status of 500 (Internal Server Error)
OrderList.vue:158  Uncaught (in promise) AxiosError: Request failed with status code 500
    at settle (settle.js:20:7)
    at XMLHttpRequest.onloadend (xhr.js:62:9)
    at Axios.request (Axios.js:46:41)
    at async getOrderList (toolIO.js:13:25)
    at async loadOrders (OrderList.vue:146:18)
client:912 [vite] connected.
```

## Additional Runtime Finding / 琛ュ厖杩愯鏃朵俊鎭?

- `frontend/vite.config.js` proxies `/api` to `http://127.0.0.1:5000`
- During investigation of the user-reported error, no process was listening on `127.0.0.1:5000`
- Direct request to `http://127.0.0.1:5000/api/tool-io-orders` failed with connection refusal until the Flask server was started
- After starting `python web_server.py`, the same order list request returned `200`
---

## Final Confirmation / 缁堟€佺‘璁?

- On March 12, 2026, the user confirmed that Bug 103 was fully resolved
- The frontend can now load test data successfully
- The follow-up detail-page `400` caused by premature transport-text generation was also addressed in the same repair chain
- Bug 103 is now considered closed
