Primary Executor: Codex
Task Type: Feature Implementation
Stage: 053
Goal: Implement tool locking mechanism to prevent duplicate applications
Execution: RUNPROMPT

## 上下文 / Context

当前系统存在严重的业务逻辑漏洞：测试用的工装在出库申请提出但未被处理时，依然可以再次提出申请。这会导致：
- 同一工装被多个订单重复占用
- 库存数据不一致
- 出库操作冲突

## 必需参考 / Required References

1. `backend/database/tool_io_queries.py` - 订单数据库操作函数
2. `backend/services/tool_io_service.py` - 订单业务逻辑服务层
3. 订单状态机定义（draft, submitted, keeper_confirmed, partially_confirmed, completed, rejected, cancelled）
4. 工装身份卡表结构 (`工装身份卡_主表`)

## 核心任务 / Core Task

实现工装锁定机制：在创建或提交订单时，检查工装是否被未完成订单占用。

## 必需工作 / Required Work

1. **添加检查函数** (`tool_io_queries.py`)
   - 实现 `check_tools_available(tool_codes: list, exclude_order_no: str = None)` 函数
   - 检查指定工装是否有未完成的订单占用（仅检查已提交的非草稿订单）
   - 占用状态包括：submitted, keeper_confirmed, partially_confirmed, transport_notified, transport_in_progress, transport_completed, final_confirmation_pending
   - 返回被占用的工装列表和订单信息

2. **修改创建订单逻辑** (`tool_io_queries.py`)
   - 在 `create_tool_io_order` 函数中，创建前调用 `check_tools_available` 检查工装可用性
   - 如果工装被占用，返回错误信息并阻止创建

3. **修改提交订单逻辑** (`tool_io_queries.py`)
   - 在 `submit_tool_io_order` 函数中，提交前再次检查工装可用性
   - 防止提交已被其他订单占用的工装

4. **释放机制**
   - 当订单完成/取消/拒绝时，订单状态变更自动释放占用（无需额外逻辑，因为状态不再是"占用"状态）

## 约束条件 / Constraints

1. 不修改数据库表结构（使用订单状态判断占用）
2. 草稿状态（draft）的订单不占用工装，只有已提交的非草稿订单才占用
3. 同一工装只能有一个进行中的订单（不论出库还是入库）
4. 必须集成到现有的 `create_tool_io_order` 和 `submit_tool_io_order` 函数中
5. 错误信息应清晰说明哪些工装被占用及关联的订单号

## 完成标准 / Completion Criteria

1. `check_tools_available` 函数正确返回被占用工装及关联订单信息
2. 创建订单时检查工装可用性，被占用时返回错误
3. 提交订单时再次检查工装可用性
4. 前端创建订单时可显示友好的错误提示
5. 代码符合项目编码规范（4空格缩进、snake_case）
6. 通过语法检查：`python -m py_compile backend/database/tool_io_queries.py`
