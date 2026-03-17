# 认证实现说明 / Authentication Implementation

## 概述 / Overview

本次实现为系统补充了第一版本地账号认证，并与既有 RBAC 设计对齐。

新增能力:

- `POST /api/auth/login` 登录接口
- `GET /api/auth/me` 当前用户接口
- Bearer Token 请求认证
- API 级权限守卫
- Vue 登录页与前端 token 注入

## 后端实现 / Backend

后端认证逻辑位于:

- `backend/services/auth_service.py`

实现细节:

- 使用 `hashlib.pbkdf2_hmac` 生成密码哈希
- 哈希格式为 `pbkdf2_sha256$iterations$salt$hash`
- 使用 Flask `SECRET_KEY` 通过 `itsdangerous` 签发 bearer token
- 每次请求通过 `Authorization: Bearer <token>` 解析当前用户
- 从 `sys_user`、`sys_user_role_rel`、`sys_role`、`sys_role_permission_rel`、`sys_permission` 加载身份与权限

## 权限接入 / Permission Enforcement

当前 API 权限映射:

- `/api/tool-io-orders` `GET` -> `order:list`
- `/api/tool-io-orders` `POST` -> `order:create`
- `/api/tool-io-orders/<order_no>` `GET` -> `order:view`
- `/api/tool-io-orders/<order_no>/submit` -> `order:submit`
- `/api/tool-io-orders/<order_no>/keeper-confirm` -> `order:keeper_confirm`
- `/api/tool-io-orders/<order_no>/final-confirm` -> `order:final_confirm`
- `/api/tool-io-orders/<order_no>/reject` -> `order:cancel`
- `/api/tool-io-orders/<order_no>/cancel` -> `order:cancel`
- `/api/tool-io-orders/<order_no>/notification-records` -> `notification:view`
- `/api/tool-io-orders/<order_no>/generate-keeper-text` -> `notification:create`
- `/api/tool-io-orders/<order_no>/generate-transport-text` -> `notification:create`
- `/api/tool-io-orders/<order_no>/notify-transport` -> `notification:send_feishu`
- `/api/tool-io-orders/<order_no>/notify-keeper` -> `notification:send_feishu`
- `/api/tools/search` -> `tool:search`
- `/api/tools/batch-query` -> `tool:view`

## 前端实现 / Frontend

前端新增:

- `frontend/src/pages/auth/LoginPage.vue`
- `frontend/src/api/auth.js`

前端变更:

- `frontend/src/store/session.js` 现在持久化 token、角色和权限
- `frontend/src/api/http.js` 自动附加 bearer token
- `frontend/src/router/index.js` 增加登录页与权限路由守卫
- `frontend/src/layouts/MainLayout.vue` 改为显示真实认证用户，不再手工编辑伪 session

## 首次管理员账号 / First Admin Bootstrap

系统使用本地账号表 `sys_user`。首次管理员需要先写入 `sys_user` 和 `sys_user_role_rel`。

先用 Python 生成密码哈希:

```powershell
@'
from backend.services.auth_service import hash_password
print(hash_password("admin123"))
'@ | python -
```

将输出的哈希值填入以下 SQL:

```sql
INSERT INTO sys_user (
    user_id, login_name, display_name, password_hash, status, created_at, created_by
)
VALUES (
    'U_ADMIN',
    'admin',
    'System Administrator',
    '<PASTE_HASH_HERE>',
    'active',
    SYSDATETIME(),
    'bootstrap'
);

INSERT INTO sys_user_role_rel (
    user_id, role_id, org_id, is_primary, status, created_at, created_by
)
VALUES (
    'U_ADMIN',
    'ROLE_SYS_ADMIN',
    NULL,
    1,
    'active',
    SYSDATETIME(),
    'bootstrap'
);
```

完成后即可使用:

- login_name: `admin`
- password: `admin123`

## 限制 / Limits

- 当前版本未实现数据范围过滤
- 当前版本未接入刷新 token
- 当前版本未实现前端细粒度按钮级权限治理，主要先覆盖路由与 API
