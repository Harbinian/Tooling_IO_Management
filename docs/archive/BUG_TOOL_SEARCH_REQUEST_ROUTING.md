# Bug 工装搜索请求路由 / Bug Tool Search Request Routing

---

## 观察到的现象 / Observed Problem

工装搜索对话框发送请求到: / The tool search dialog sent requests to:

- `/api/tools/search`

观察到的浏览器行为: / Observed browser behavior:

- 响应状态: `200` / response status: `200`
- 响应内容类型: `text/html` / response content-type: `text/html`
- 前端随后报告工装搜索失败 / frontend then reported tool search failure

这意味着请求没有到达后端 API，而是被前端开发服务器服务。 / This meant the request was not reaching the backend API and instead was being served by the frontend development server.

---

## 根本原因 / Root Cause

前端 HTTP 客户端配置为使用相对 API 基础路径: / The frontend HTTP client was configured to use a relative API base path:

- `baseURL: '/api'`

只有当开发服务器将 `/api` 请求代理到 Flask 后端时，这才是正确的。 / This is correct only if the development server proxies `/api` requests to the Flask backend.

然而 `frontend/vite.config.js` 没有定义任何 `/api` 代理。 / However `frontend/vite.config.js` did not define any `/api` proxy.

所以在开发模式下: / So in development mode:

1. 浏览器向 Vite 开发服务器请求 `/api/tools/search` / the browser requested `/api/tools/search` from the Vite dev server
2. Vite 没有将请求代理到 `http://127.0.0.1:5000` / Vite did not proxy the request to `http://127.0.0.1:5000`
3. 请求回退到前端应用处理器 / the request fell back to the frontend app handler
4. 返回 HTML 而非 JSON / HTML was returned instead of JSON

后端路由本身已经正确: / The backend route itself was already correct:

- `GET /api/tools/search`

---

## 修改的文件 / Files Modified

- `frontend/vite.config.js`
- `frontend/src/api/http.js`

---

## 应用的路由修复 / Routing Fix Applied

### 1. 添加 Vite 开发服务器代理 / 1. Added Vite dev server proxy

`frontend/vite.config.js` 现在代理: / `frontend/vite.config.js` now proxies:

- `/api` -> `http://127.0.0.1:5000`

通过以下方式支持环境变量覆盖: / with support for environment override via:

- `VITE_API_PROXY_TARGET`

### 2. 规范化前端 API 基础 URL 处理 / 2. Normalized frontend API base URL handling

`frontend/src/api/http.js` 现在使用: / `frontend/src/api/http.js` now uses:

- `VITE_API_BASE_URL`
- 回退 `/api` / fallback `/api`

并保持现有前端架构完整。 / and keeps the existing frontend architecture intact.

它还发送: / It also sends:

- `Accept: application/json`

以使预期的响应类型明确。 / to make the expected response type explicit.

---

## 前端/后端路径对齐 / Frontend / Backend Path Alignment

前端请求路径: / Frontend request path:

- `/api/tools/search`

后端 Flask 路由: / Backend Flask route:

- `/api/tools/search`

修复后的开发路由: / Development routing after fix:

- 浏览器 -> Vite 开发服务器 `:5173` / browser -> Vite dev server `:5173`
- Vite 代理 -> Flask 后端 `:5000` / Vite proxy -> Flask backend `:5000`
- Flask 返回 JSON / Flask returns JSON
- 对话框接收 JSON 数据并渲染行 / dialog receives JSON data and renders rows

---

## 验证结果 / Verification Results

通过代码和运行时配置验证: / Verified from code and runtime configuration:

- Vite 配置现在暴露代理键 `/api` / Vite config now exposes proxy key `/api`
- 代理目标解析为 `http://127.0.0.1:5000` / proxy target resolves to `http://127.0.0.1:5000`
- 前端 HTTP 模块成功加载 / frontend HTTP module loads successfully
- 前端生产构建通过 `npm run build` 成功 / frontend production build succeeds with `npm run build`
- 后端路由注册保持与 `/api/tools/search` 对齐 / backend route registration remains aligned with `/api/tools/search`

---

## 备注 / Notes

此修复有意保持最小化: / This fix is intentionally minimal:

- 没有更改后端搜索逻辑 / no backend search logic was changed
- 没有重新设计不相关的前端模块 / no unrelated frontend modules were redesigned
- 问题在实际发生的请求路由层解决 / the issue was resolved at the request routing layer where it actually occurred
