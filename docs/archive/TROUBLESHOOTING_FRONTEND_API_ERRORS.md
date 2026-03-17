# 前端 API 错误故障排除 / Frontend API Error Troubleshooting

## 范围 / Scope

本文记录了在验证工装出入库 Vue 应用时看到的最近前端运行时错误以及诊断方式。

This note records the recent frontend runtime errors seen while validating the Tool IO Vue application and how they were diagnosed.

## 案例 1：订单列表页面返回 `500` / Case 1: Order List Page returned `500`

### 用户可见的症状 / User-visible symptom

Vite 前端请求：

The Vite frontend requested:

- `GET /api/tool-io-orders?keyword=&order_type=&order_status=&initiator_id=&keeper_id=&page_no=1&page_size=20`

浏览器报告 `500`。

and the browser reported a `500`.

### 确认的运行时发现 / Confirmed runtime finding

前端开发服务器将 `/api` 代理到：

The frontend dev server proxies `/api` to:

- `http://127.0.0.1:5000`

调查时，没有进程在端口 `5000` 上监听，因此代理目标不可用。

At investigation time, no process was listening on port `5000`, so the proxy target was unavailable.

启动后端后：

After starting the backend with:

```powershell
python web_server.py
```

相同请求返回 `200`。

the same request returned `200`.

### 实际检查 / Practical check

如果列表页面在本地开发中突然再次失败，请先验证以下内容：

If the list page suddenly starts failing again in local development, verify these first:

1. Vite 开发服务器运行在 `5173` 上 / Vite dev server is running on `5173`
2. Flask 后端运行在 `5000` 上 / Flask backend is running on `5000`
3. `frontend/vite.config.js` 仍然将 `/api` 代理到预期的后端 / `frontend/vite.config.js` still proxies `/api` to the intended backend

## 案例 2：订单详情页请求 `generate-transport-text` 得到 `400` / Case 2: Order Detail page requested `generate-transport-text` and got `400`

### 用户可见的症状 / User-visible symptom

浏览器报告：

The browser reported:

```text
GET /api/tool-io-orders/TO-OUT-20260311-001/generate-transport-text 400 (BAD REQUEST)
```

控制台显示来自 `OrderDetail.vue` 的 Axios 错误。

and the console showed an Axios error from `OrderDetail.vue`.

### 根本原因 / Root cause

`frontend/src/pages/tool-io/OrderDetail.vue` 加载订单详情页后无条件请求：

`frontend/src/pages/tool-io/OrderDetail.vue` loaded the order detail page and unconditionally requested:

- `generateKeeperText(orderNo)`
- `generateTransportText(orderNo)`

对于像 `TO-OUT-20260311-001` 这样的草稿订单，后端正确地拒绝生成运输文本，因为还没有已确认的项目。

For draft orders such as `TO-OUT-20260311-001`, the backend correctly rejects transport text generation because there are no approved items yet.

后端行为确认：

Backend behavior confirmed:

```python
generate_transport_text('TO-OUT-20260311-001')
-> {'success': False, 'error': '没有已确认的工装'}
```

所以 `400` 是前端调用时机问题，不是后端 bug。

So the `400` was a frontend call-timing problem, not a backend bug.

### 应用的修复 / Fix applied

`OrderDetail.vue` 现在：

`OrderDetail.vue` now:

1. 首先加载订单详情 / loads order detail first
2. 检查订单状态 / 已确认数量 / checks order status / approved count
3. 仅在实际符合条件时才请求运输预览 / only requests transport preview when the order is actually eligible

### 前端使用的资格规则 / Eligibility rule used in frontend

仅在以下任一条件满足时才请求运输预览：

Transport preview is requested only when either:

- `approvedCount > 0`，或 / or
- `orderStatus` 是以下之一： / is one of:
  - `keeper_confirmed` / 保管员已确认
  - `partially_confirmed` / 部分已确认
  - `transport_notified` / 运输已通知

## 推荐的调试序列 / Recommended debugging sequence

本地开发中出现前端 API 错误时：

When a frontend API error appears in local development:

1. 复制浏览器请求 URL 和状态码 / Copy the exact browser request URL and status code
2. 验证后端端口是否实际在监听 / Verify whether the backend port is actually listening
3. 使用 Flask `test_client()` 或直接 HTTP 复现相同请求 / Reproduce the same request with Flask `test_client()` or direct HTTP
4. 检查前端是否在有效的业务状态下调用 API / Check whether the frontend is calling the API under a valid business state
5. 仅在运行时复现确认相同失败路径后才视为后端缺陷 / Only treat it as a backend defect after runtime reproduction confirms the same failure path
