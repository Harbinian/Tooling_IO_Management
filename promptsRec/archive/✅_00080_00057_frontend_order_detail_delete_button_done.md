Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 057
Goal: Add delete button to order detail page for admin role
Dependencies: 056
Execution: RUNPROMPT

---

## Context

在管理员删除订单功能完成后，需要在前端订单详情页添加删除按钮。

需求：
1. 在订单详情页添加删除按钮（仅管理员可见）
2. 添加删除确认对话框
3. 调用删除 API

## Required References

1. `frontend/src/pages/OrderDetail.vue` - 订单详情页组件
2. `frontend/src/api/orders.js` - 订单 API 调用
3. `frontend/src/store/` - 状态管理（检查用户角色）

## Core Task

在订单详情页为管理员添加删除订单的入口。

## Required Work

1. **添加删除按钮**:
   - 在订单详情页操作区域添加删除按钮
   - 按钮仅对 admin 角色可见

2. **添加确认对话框**:
   - 使用 Element Plus 的确认对话框
   - 显示警告信息："确定要删除此订单吗？此操作不可恢复。"

3. **调用删除 API**:
   - 调用 `DELETE /api/tool-io-orders/<order_no>`
   - 删除成功后跳转到订单列表页

## Constraints

- 遵循现有的 Element Plus 组件风格
- 按钮样式使用危险色（红色）
- 删除按钮位置应在页面底部操作栏
- 不要破坏现有的页面布局和功能

## Completion Criteria

- [ ] 管理员可以看到删除按钮
- [ ] 非管理员看不到删除按钮
- [ ] 点击删除按钮弹出确认对话框
- [ ] 确认后调用删除 API
- [ ] 删除成功跳转列表页
- [ ] 前端构建通过
