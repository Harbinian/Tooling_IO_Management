# SQL 中文表名/字段核查报告

- 核查时间: 2026-03-26
- 核查范围: `backend/**/*.py`
- 核查命令:
  - `rg -n -P "(SELECT|INSERT|UPDATE|DELETE|FROM|JOIN|INTO|WHERE).*[\p{Han}]" backend -g "*.py"`

## 结论

项目中**仍包含**中文表名/字段 SQL 语句。

- 命中总数: 50
- 命中文件数: 8

## 命中分布（按文件）

| 命中数 | 文件 |
|---:|---|
| 21 | `backend/database/core/database_manager.py` |
| 16 | `backend/database/acceptance_queries.py` |
| 6 | `backend/database/repositories/dispatch_repository.py` |
| 2 | `backend/database/repositories/acceptance_repository.py` |
| 2 | `backend/database/repositories/tpitr_repository.py` |
| 1 | `backend/services/order_query_service.py` |
| 1 | `backend/services/notification_service.py` |
| 1 | `backend/database/schema/column_names.py` |

## 重点发现

1. 外部系统中文表/字段仍大量存在（符合现有系统现实）
- 示例: `工装验收管理_主表`、`工装定检派工_明细`、`工艺装备返工申请单_主表`、`TPITR_主表_V11`
- 主要集中在:
  - `backend/database/core/database_manager.py`
  - `backend/database/acceptance_queries.py`
  - `backend/database/repositories/dispatch_repository.py`

2. 疑似遗留不一致（建议优先核对）
- `backend/services/notification_service.py:327`
- SQL 使用 `FROM tool_io_notification`，但条件写为 `WHERE 出入库单号 = ?`
- 若 `tool_io_notification` 已统一英文字段，该处可能导致查询失败或行为不一致。

3. 业务服务中仍有中文表名直查
- `backend/services/order_query_service.py:137` 使用 `FROM 工装主数据`
- 需确认是否属于外部库只读依赖，或应切换到统一 repository/映射层。

## 逐条命中清单（原始扫描）

```text
backend\services\order_query_service.py:137:        FROM 工装主数据
backend\services\notification_service.py:327:        WHERE 出入库单号 = ?
backend\database\acceptance_queries.py:24:                "SELECT 派工号 FROM 工装验收管理_主表 WHERE 派工号 = ?",
backend\database\acceptance_queries.py:33:                    INSERT INTO 工装验收管理_主表 (
backend\database\acceptance_queries.py:59:            INSERT INTO 工装验收管理_主表 (
backend\database\acceptance_queries.py:76:            UPDATE 工装验收管理_主表
backend\database\acceptance_queries.py:78:            WHERE 派工号 = ?
backend\database\acceptance_queries.py:93:            IF EXISTS (SELECT 1 FROM 工装验收管理_主表 WHERE 派工号 = ?)
backend\database\acceptance_queries.py:94:                UPDATE 工装验收管理_主表 SET
backend\database\acceptance_queries.py:97:                WHERE 派工号 = ?
backend\database\acceptance_queries.py:99:                INSERT INTO 工装验收管理_主表 (
backend\database\acceptance_queries.py:121:            SELECT 派工号, 表编号, 序列号, 工装图号, 工装名称,
backend\database\acceptance_queries.py:125:            FROM 工装验收管理_主表
backend\database\acceptance_queries.py:126:            WHERE 验收状态 IN ('待检查', '检查中', '待验收')
backend\database\acceptance_queries.py:162:            UPDATE 工装验收管理_主表
backend\database\acceptance_queries.py:166:            WHERE 派工号 = ?
backend\database\acceptance_queries.py:179:            UPDATE 工装验收管理_主表
backend\database\acceptance_queries.py:181:            WHERE 派工号 = ?
backend\database\core\database_manager.py:212:            WHERE m.定检有效截止 IS NOT NULL
backend\database\core\database_manager.py:271:            FROM 工装定检派工_明细 d
backend\database\core\database_manager.py:272:            LEFT JOIN 工装定检派工_主表 m ON d.ExcelServerRCID = m.ExcelServerRCID AND d.ExcelServerWIID = m.ExcelServerWIID
backend\database\core\database_manager.py:317:            FROM TPITR_主表_V11
backend\database\core\database_manager.py:366:                FROM 工装验收管理_主表 m
backend\database\core\database_manager.py:405:                FROM 不合格工装通知单_主表 m
backend\database\core\database_manager.py:439:                SELECT 序列号, 工装名称, 工装图号, ExcelServerRCID, ExcelServerWIID
backend\database\core\database_manager.py:440:                FROM 工装定检记录_主表 ORDER BY 序号 DESC
backend\database\core\database_manager.py:456:                SELECT 序列号, 工装名称, 工装图号, ExcelServerRCID, ExcelServerWIID
backend\database\core\database_manager.py:457:                FROM 工装返修记录_主表 ORDER BY 序号 DESC
backend\database\core\database_manager.py:472:            SELECT r.OA申请单编号, r.派工号, r.序列号, r.工装图号, r.工装名称,
backend\database\core\database_manager.py:475:            FROM 工艺装备返工申请单_主表 r
backend\database\core\database_manager.py:476:            LEFT JOIN Tooling_ID_Main t ON r.序列号 = t.序列号
backend\database\core\database_manager.py:477:            WHERE r.OA申请单编号 IS NOT NULL
backend\database\core\database_manager.py:479:              AND NOT EXISTS (SELECT 1 FROM 工装验收管理_主表 m WHERE m.派工号 = r.派工号)
backend\database\core\database_manager.py:489:            SELECT n.编号, n.派工号, n.工装序列号, n.工装图号, n.工装名称,
backend\database\core\database_manager.py:492:            FROM 工艺装备申请单_主表 n
backend\database\core\database_manager.py:493:            WHERE n.编号 IS NOT NULL
backend\database\core\database_manager.py:496:              AND NOT EXISTS (SELECT 1 FROM 工装验收管理_主表 m WHERE m.派工号 = n.派工号)
backend\database\core\database_manager.py:498:                  SELECT 1 FROM 工艺装备返工申请单_主表 r
backend\database\core\database_manager.py:499:                  WHERE r.派工号 = n.派工号
backend\database\schema\column_names.py:16:    sql = f"SELECT {ORDER_CHINESE_COLUMNS['order_no']} FROM 工装出入库单_主表"
backend\database\repositories\acceptance_repository.py:56:            FROM 工装验收管理_主表 m
backend\database\repositories\acceptance_repository.py:57:            WHERE m.派工号 = ?
backend\database\repositories\dispatch_repository.py:52:            FROM 工装定检派工_明细 d
backend\database\repositories\dispatch_repository.py:53:            LEFT JOIN 工装定检派工_主表 m ON d.ExcelServerRCID = m.ExcelServerRCID AND d.ExcelServerWIID = m.ExcelServerWIID
backend\database\repositories\dispatch_repository.py:54:            WHERE d.序列号 = ?
backend\database\repositories\dispatch_repository.py:78:            FROM 工装定检派工_明细 d
backend\database\repositories\dispatch_repository.py:79:            LEFT JOIN 工装定检派工_主表 m ON d.ExcelServerRCID = m.ExcelServerRCID AND d.ExcelServerWIID = m.ExcelServerWIID
backend\database\repositories\dispatch_repository.py:80:            WHERE d.完成日期 IS NULL OR d.申请人确认 IS NULL
backend\database\repositories\tpitr_repository.py:60:            FROM TPITR_主表_V11
backend\database\repositories\tpitr_repository.py:61:            WHERE 工装图号 = ?
```

## 建议

1. 先修复 `notification_service.py:327` 的字段名一致性（高优先级，低成本）。
2. 对 `order_query_service.py` 建立来源标注：外部依赖则保留并加注释；内部表则迁移到英文字段映射层。
3. 对 `database_manager.py`/`acceptance_queries.py` 建立“外部中文表白名单”，避免后续误判为回归问题。