Primary Executor: Codex
Task Type: Bug Fix
Priority: P0
Stage: 131
Goal: Fix order creation returning 400 due to SQL encoding corruption in check_tools_in_draft_orders
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

在浏览器中创建订单时，POST /api/tool-io-orders 返回 400 BAD REQUEST 错误。

后端日志显示：
```
The SQL contains 0 parameter markers, but 1 parameters were supplied
```

错误发生在 `check_tools_in_draft_orders` 方法中。

---

## Required References / 必需参考

- `backend/database/repositories/tool_repository.py` - 第 269-330 行 `check_tools_in_draft_orders` 方法
- `backend/database/repositories/tool_repository.py` - 第 210-267 行 `check_tools_available` 方法（正确编码的参考）

---

## Core Task / 核心任务

修复 `tool_repository.py` 中 `check_tools_in_draft_orders` 方法的中文字符编码损坏问题。

当前该方法中的中文字符已经损坏：
- `序列号` 变成 `搴忓垪鍙穄`
- `工装名称` 变成 `宸ヨ祫鍚嶇О`
- `出入库单号` 变成 `鍑哄叆搴撳崟鍙穄`
- `发起人姓名` 变成 `鍙戣捣浜哄拰鍚峕`
- `创建时间` 变成 `鍒涘缓鏃堕棿`
- `工装出入库单_明细` 变成 `宸ヨ祫鍑哄叆搴撳崟_鏄庣粏`
- `工装出入库单_主表` 变成 `宸ヨ祫鍑哄叆搴撳崟_涓昏〃`
- `单据状态` 变成 `鍗曟嵁鐘舵€乚`

而同一文件中 `check_tools_available` 方法（第 210-267 行）的中文字符是正确的，可以作为参考。

---

## Required Work / 必需工作

1. 读取 `backend/database/repositories/tool_repository.py` 文件
2. 定位 `check_tools_in_draft_orders` 方法（第 269 行开始）
3. 将该方法中所有损坏的中文字符替换为正确的中文
4. 确保 SQL 语句中的列名和表名与数据库 Schema 一致
5. 运行语法检查：`python -m py_compile backend/database/repositories/tool_repository.py`

**修复后的 SQL 应该是：**
```sql
SELECT
    detail.[序列号] AS tool_code,
    detail.[工装名称] AS tool_name,
    main.[出入库单号] AS order_no,
    main.[发起人姓名] AS initiator_name,
    main.[创建时间] AS created_at
FROM [工装出入库单_明细] AS detail
INNER JOIN [工装出入库单_主表] AS main
    ON main.[出入库单号] = detail.[出入库单号]
WHERE detail.[序列号] IN ({code_placeholders})
  AND main.[IS_DELETED] = 0
  AND main.[单据状态] = 'draft'
ORDER BY main.[创建时间] DESC, main.[出入库单号] DESC
```

---

## Constraints / 约束条件

- 只修复编码损坏问题，不要修改业务逻辑
- 保持方法签名和返回值结构不变
- SQL 语句结构必须与 `check_tools_available` 方法保持一致
- 必须使用 UTF-8 编码保存文件

---

## Completion Criteria / 完成标准

1. `python -m py_compile backend/database/repositories/tool_repository.py` 执行成功无错误
2. `check_tools_in_draft_orders` 方法中的所有中文字符正确显示
3. 订单创建 API 返回 201 而不是 400
4. 前端可以正常创建订单
