-- ============================================================
-- 数据库表名/字段名英文化迁移脚本 V2
-- 目标：将中文表名/字段名迁移到英文
--
-- 【重要】绝对禁止对 工装身份卡_主表 进行任何操作！
--
-- 变更说明 V2:
--   - 使用显式列名而非 SELECT *
--   - 跳过始终为NULL的列 (运输人ID, 运输人姓名)
--   - 直接创建英文列名
-- ============================================================

SET XACT_ABORT ON;
BEGIN TRANSACTION;

-- ============================================================
-- 步骤1：创建映射表（记录旧名到新名的映射）
-- ============================================================
IF OBJECT_ID(N'table_english_mappings', N'U') IS NULL
BEGIN
    CREATE TABLE table_english_mappings (
        id INT IDENTITY(1,1) PRIMARY KEY,
        original_table NVARCHAR(100) NOT NULL,
        english_table NVARCHAR(100) NOT NULL,
        original_column NVARCHAR(100) NOT NULL,
        english_column NVARCHAR(100) NOT NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT UX_mapping UNIQUE(original_table, original_column)
    );

    -- 插入主表映射
    INSERT INTO table_english_mappings (original_table, english_table, original_column, english_column) VALUES
    (N'工装出入库单_主表', N'tool_io_order', N'id', N'id'),
    (N'工装出入库单_主表', N'tool_io_order', N'出入库单号', N'order_no'),
    (N'工装出入库单_主表', N'tool_io_order', N'单据类型', N'order_type'),
    (N'工装出入库单_主表', N'tool_io_order', N'单据状态', N'order_status'),
    (N'工装出入库单_主表', N'tool_io_order', N'发起人ID', N'initiator_id'),
    (N'工装出入库单_主表', N'tool_io_order', N'发起人姓名', N'initiator_name'),
    (N'工装出入库单_主表', N'tool_io_order', N'发起人角色', N'initiator_role'),
    (N'工装出入库单_主表', N'tool_io_order', N'部门', N'department'),
    (N'工装出入库单_主表', N'tool_io_order', N'项目代号', N'project_code'),
    (N'工装出入库单_主表', N'tool_io_order', N'用途', N'usage_purpose'),
    (N'工装出入库单_主表', N'tool_io_order', N'计划使用时间', N'planned_use_time'),
    (N'工装出入库单_主表', N'tool_io_order', N'计划归还时间', N'planned_return_time'),
    (N'工装出入库单_主表', N'tool_io_order', N'目标位置ID', N'target_location_id'),
    (N'工装出入库单_主表', N'tool_io_order', N'目标位置文本', N'target_location_text'),
    (N'工装出入库单_主表', N'tool_io_order', N'保管员ID', N'keeper_id'),
    (N'工装出入库单_主表', N'tool_io_order', N'保管员姓名', N'keeper_name'),
    (N'工装出入库单_主表', N'tool_io_order', N'运输类型', N'transport_type'),
    (N'工装出入库单_主表', N'tool_io_order', N'运输AssigneeID', N'transport_operator_id'),
    (N'工装出入库单_主表', N'tool_io_order', N'运输AssigneeName', N'transport_operator_name'),
    (N'工装出入库单_主表', N'tool_io_order', N'保管员需求文本', N'keeper_requirement_text'),
    (N'工装出入库单_主表', N'tool_io_order', N'运输通知文本', N'transport_notice_text'),
    (N'工装出入库单_主表', N'tool_io_order', N'微信复制文本', N'wechat_copy_text'),
    (N'工装出入库单_主表', N'tool_io_order', N'保管员确认时间', N'keeper_confirm_time'),
    (N'工装出入库单_主表', N'tool_io_order', N'运输通知时间', N'transport_notify_time'),
    (N'工装出入库单_主表', N'tool_io_order', N'最终确认时间', N'final_confirm_time'),
    (N'工装出入库单_主表', N'tool_io_order', N'工装数量', N'tool_quantity'),
    (N'工装出入库单_主表', N'tool_io_order', N'已确认数量', N'confirmed_count'),
    (N'工装出入库单_主表', N'tool_io_order', N'最终确认人', N'final_confirm_by'),
    (N'工装出入库单_主表', N'tool_io_order', N'驳回原因', N'reject_reason'),
    (N'工装出入库单_主表', N'tool_io_order', N'取消原因', N'cancel_reason'),
    (N'工装出入库单_主表', N'tool_io_order', N'备注', N'remark'),
    (N'工装出入库单_主表', N'tool_io_order', N'org_id', N'org_id'),
    (N'工装出入库单_主表', N'tool_io_order', N'创建时间', N'created_at'),
    (N'工装出入库单_主表', N'tool_io_order', N'修改时间', N'updated_at'),
    (N'工装出入库单_主表', N'tool_io_order', N'创建人', N'created_by'),
    (N'工装出入库单_主表', N'tool_io_order', N'修改人', N'updated_by'),
    (N'工装出入库单_主表', N'tool_io_order', N'IS_DELETED', N'is_deleted');

    -- 插入明细表映射
    INSERT INTO table_english_mappings (original_table, english_table, original_column, english_column) VALUES
    (N'工装出入库单_明细', N'tool_io_order_item', N'id', N'id'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'出入库单号', N'order_no'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'工装ID', N'tool_id'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'序列号', N'tool_code'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'工装名称', N'tool_name'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'工装图号', N'drawing_no'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'机型', N'spec_model'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'申请数量', N'apply_qty'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'确认数量', N'confirmed_qty'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'明细状态', N'item_status'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'工装快照状态', N'tool_snapshot_status'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'工装快照位置ID', N'tool_snapshot_location_id'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'工装快照位置文本', N'tool_snapshot_location_text'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'保管员确认位置ID', N'keeper_confirm_location_id'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'保管员确认位置文本', N'keeper_confirm_location_text'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'保管员检查结果', N'keeper_check_result'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'保管员检查备注', N'keeper_check_remark'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'归还检查结果', N'return_check_result'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'归还检查备注', N'return_check_remark'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'确认时间', N'confirm_time'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'出入库完成时间', N'io_complete_time'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'排序号', N'sort_order'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'创建时间', N'created_at'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'修改时间', N'updated_at'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'确认人', N'confirm_by'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'确认人ID', N'confirm_by_id'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'确认人姓名', N'confirm_by_name'),
    (N'工装出入库单_明细', N'tool_io_order_item', N'驳回原因', N'reject_reason');

    -- 插入操作日志表映射
    INSERT INTO table_english_mappings (original_table, english_table, original_column, english_column) VALUES
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'id', N'id'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'出入库单号', N'order_no'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'明细ID', N'item_id'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'操作类型', N'operation_type'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'操作人ID', N'operator_id'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'操作人姓名', N'operator_name'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'操作人角色', N'operator_role'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'变更前状态', N'from_status'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'变更后状态', N'to_status'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'操作内容', N'operation_content'),
    (N'工装出入库单_操作日志', N'tool_io_operation_log', N'操作时间', N'operation_time');

    -- 插入通知记录表映射
    INSERT INTO table_english_mappings (original_table, english_table, original_column, english_column) VALUES
    (N'工装出入库单_通知记录', N'tool_io_notification', N'id', N'id'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'出入库单号', N'order_no'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'通知类型', N'notify_type'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'通知渠道', N'notify_channel'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'接收人', N'receiver'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'通知标题', N'notify_title'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'通知内容', N'notify_content'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'复制文本', N'copy_text'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'发送状态', N'send_status'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'发送时间', N'send_time'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'发送结果', N'send_result'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'重试次数', N'retry_count'),
    (N'工装出入库单_通知记录', N'tool_io_notification', N'创建时间', N'created_at');

    -- 插入位置表映射
    INSERT INTO table_english_mappings (original_table, english_table, original_column, english_column) VALUES
    (N'工装出入库单_位置', N'tool_io_location', N'id', N'id'),
    (N'工装出入库单_位置', N'tool_io_location', N'位置编码', N'location_code'),
    (N'工装出入库单_位置', N'tool_io_location', N'位置名称', N'location_name'),
    (N'工装出入库单_位置', N'tool_io_location', N'位置描述', N'location_desc'),
    (N'工装出入库单_位置', N'tool_io_location', N'库区', N'warehouse_area'),
    (N'工装出入库单_位置', N'tool_io_location', N'库位', N'storage_slot'),
    (N'工装出入库单_位置', N'tool_io_location', N'货架', N'shelf'),
    (N'工装出入库单_位置', N'tool_io_location', N'备注', N'remark');

    -- 插入运输异常记录表映射
    INSERT INTO table_english_mappings (original_table, english_table, original_column, english_column) VALUES
    (N'工装运输异常记录', N'tool_io_transport_issue', N'id', N'id'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'异常单号', N'order_no'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'异常类型', N'issue_type'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'异常描述', N'description'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'异常图片URL', N'image_urls'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'上报人ID', N'reporter_id'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'上报人姓名', N'reporter_name'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'上报时间', N'report_time'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'处理状态', N'status'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'处理人ID', N'handler_id'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'处理人姓名', N'handler_name'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'处理时间', N'handle_time'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'处理回复', N'handle_reply'),
    (N'工装运输异常记录', N'tool_io_transport_issue', N'创建时间', N'created_at');

    PRINT 'Step 1: Mappings table created successfully';
END
ELSE
BEGIN
    PRINT 'Step 1: Mappings table already exists, skipping...';
END


-- ============================================================
-- 步骤2：使用显式列名创建新英文表（跳过NULL列）
-- ============================================================

-- 2.1 主表
-- 注意：跳过运输人ID和运输人姓名（始终为NULL），只迁移运输AssigneeID/AssigneeName
IF OBJECT_ID(N'tool_io_order', N'U') IS NULL
BEGIN
    SELECT
        [id] AS id,
        [出入库单号] AS order_no,
        [单据类型] AS order_type,
        [单据状态] AS order_status,
        [发起人ID] AS initiator_id,
        [发起人姓名] AS initiator_name,
        [发起人角色] AS initiator_role,
        [部门] AS department,
        [项目代号] AS project_code,
        [用途] AS usage_purpose,
        [计划使用时间] AS planned_use_time,
        [计划归还时间] AS planned_return_time,
        [目标位置ID] AS target_location_id,
        [目标位置文本] AS target_location_text,
        [保管员ID] AS keeper_id,
        [保管员姓名] AS keeper_name,
        [运输类型] AS transport_type,
        [运输AssigneeID] AS transport_operator_id,
        [运输AssigneeName] AS transport_operator_name,
        [保管员需求文本] AS keeper_requirement_text,
        [运输通知文本] AS transport_notice_text,
        [微信复制文本] AS wechat_copy_text,
        [保管员确认时间] AS keeper_confirm_time,
        [运输通知时间] AS transport_notify_time,
        [最终确认时间] AS final_confirm_time,
        [工装数量] AS tool_quantity,
        [已确认数量] AS confirmed_count,
        [最终确认人] AS final_confirm_by,
        [驳回原因] AS reject_reason,
        [取消原因] AS cancel_reason,
        [备注] AS remark,
        [org_id] AS org_id,
        [创建时间] AS created_at,
        [修改时间] AS updated_at,
        [创建人] AS created_by,
        [修改人] AS updated_by,
        [IS_DELETED] AS is_deleted
    INTO tool_io_order
    FROM 工装出入库单_主表;

    PRINT 'Step 2.1: tool_io_order table created with explicit columns';
END
ELSE
BEGIN
    PRINT 'Step 2.1: tool_io_order already exists, skipping...';
END

-- 2.2 明细表
IF OBJECT_ID(N'tool_io_order_item', N'U') IS NULL
BEGIN
    SELECT
        [id] AS id,
        [出入库单号] AS order_no,
        [工装ID] AS tool_id,
        [序列号] AS tool_code,
        [工装名称] AS tool_name,
        [工装图号] AS drawing_no,
        [机型] AS spec_model,
        [申请数量] AS apply_qty,
        [确认数量] AS confirmed_qty,
        [明细状态] AS item_status,
        [工装快照状态] AS tool_snapshot_status,
        [工装快照位置ID] AS tool_snapshot_location_id,
        [工装快照位置文本] AS tool_snapshot_location_text,
        [保管员确认位置ID] AS keeper_confirm_location_id,
        [保管员确认位置文本] AS keeper_confirm_location_text,
        [保管员检查结果] AS keeper_check_result,
        [保管员检查备注] AS keeper_check_remark,
        [归还检查结果] AS return_check_result,
        [归还检查备注] AS return_check_remark,
        [确认时间] AS confirm_time,
        [出入库完成时间] AS io_complete_time,
        [排序号] AS sort_order,
        [创建时间] AS created_at,
        [修改时间] AS updated_at,
        [确认人] AS confirm_by,
        [确认人ID] AS confirm_by_id,
        [确认人姓名] AS confirm_by_name,
        [驳回原因] AS reject_reason
    INTO tool_io_order_item
    FROM 工装出入库单_明细;

    PRINT 'Step 2.2: tool_io_order_item table created';
END
ELSE
BEGIN
    PRINT 'Step 2.2: tool_io_order_item already exists, skipping...';
END

-- 2.3 操作日志表
IF OBJECT_ID(N'tool_io_operation_log', N'U') IS NULL
BEGIN
    SELECT
        [id] AS id,
        [出入库单号] AS order_no,
        [明细ID] AS item_id,
        [操作类型] AS operation_type,
        [操作人ID] AS operator_id,
        [操作人姓名] AS operator_name,
        [操作人角色] AS operator_role,
        [变更前状态] AS from_status,
        [变更后状态] AS to_status,
        [操作内容] AS operation_content,
        [操作时间] AS operation_time
    INTO tool_io_operation_log
    FROM 工装出入库单_操作日志;

    PRINT 'Step 2.3: tool_io_operation_log table created';
END
ELSE
BEGIN
    PRINT 'Step 2.3: tool_io_operation_log already exists, skipping...';
END

-- 2.4 通知记录表
IF OBJECT_ID(N'tool_io_notification', N'U') IS NULL
BEGIN
    SELECT
        [id] AS id,
        [出入库单号] AS order_no,
        [通知类型] AS notify_type,
        [通知渠道] AS notify_channel,
        [接收人] AS receiver,
        [通知标题] AS notify_title,
        [通知内容] AS notify_content,
        [复制文本] AS copy_text,
        [发送状态] AS send_status,
        [发送时间] AS send_time,
        [发送结果] AS send_result,
        [重试次数] AS retry_count,
        [创建时间] AS created_at
    INTO tool_io_notification
    FROM 工装出入库单_通知记录;

    PRINT 'Step 2.4: tool_io_notification table created';
END
ELSE
BEGIN
    PRINT 'Step 2.4: tool_io_notification already exists, skipping...';
END

-- 2.5 位置表
IF OBJECT_ID(N'tool_io_location', N'U') IS NULL
BEGIN
    SELECT
        [id] AS id,
        [位置编码] AS location_code,
        [位置名称] AS location_name,
        [位置描述] AS location_desc,
        [库区] AS warehouse_area,
        [库位] AS storage_slot,
        [货架] AS shelf,
        [备注] AS remark
    INTO tool_io_location
    FROM 工装出入库单_位置;

    PRINT 'Step 2.5: tool_io_location table created';
END
ELSE
BEGIN
    PRINT 'Step 2.5: tool_io_location already exists, skipping...';
END

-- 2.6 运输异常记录表
IF OBJECT_ID(N'tool_io_transport_issue', N'U') IS NULL
BEGIN
    SELECT
        [id] AS id,
        [异常单号] AS order_no,
        [异常类型] AS issue_type,
        [异常描述] AS description,
        [异常图片URL] AS image_urls,
        [上报人ID] AS reporter_id,
        [上报人姓名] AS reporter_name,
        [上报时间] AS report_time,
        [处理状态] AS status,
        [处理人ID] AS handler_id,
        [处理人姓名] AS handler_name,
        [处理时间] AS handle_time,
        [处理回复] AS handle_reply,
        [创建时间] AS created_at
    INTO tool_io_transport_issue
    FROM 工装运输异常记录;

    PRINT 'Step 2.6: tool_io_transport_issue table created';
END
ELSE
BEGIN
    PRINT 'Step 2.6: tool_io_transport_issue already exists, skipping...';
END


-- ============================================================
-- 步骤3：创建视图别名（保持向后兼容）
-- ============================================================

-- 3.1 主表视图
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = N'工装出入库单_主表')
BEGIN
    EXEC('CREATE VIEW 工装出入库单_主表 AS SELECT * FROM tool_io_order');
    PRINT 'Step 3.1: View 工装出入库单_主表 created';
END
ELSE
BEGIN
    PRINT 'Step 3.1: View 工装出入库单_主表 already exists, skipping...';
END

-- 3.2 明细表视图
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = N'工装出入库单_明细')
BEGIN
    EXEC('CREATE VIEW 工装出入库单_明细 AS SELECT * FROM tool_io_order_item');
    PRINT 'Step 3.2: View 工装出入库单_明细 created';
END
ELSE
BEGIN
    PRINT 'Step 3.2: View 工装出入库单_明细 already exists, skipping...';
END

-- 3.3 操作日志视图
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = N'工装出入库单_操作日志')
BEGIN
    EXEC('CREATE VIEW 工装出入库单_操作日志 AS SELECT * FROM tool_io_operation_log');
    PRINT 'Step 3.3: View 工装出入库单_操作日志 created';
END
ELSE
BEGIN
    PRINT 'Step 3.3: View 工装出入库单_操作日志 already exists, skipping...';
END

-- 3.4 通知记录视图
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = N'工装出入库单_通知记录')
BEGIN
    EXEC('CREATE VIEW 工装出入库单_通知记录 AS SELECT * FROM tool_io_notification');
    PRINT 'Step 3.4: View 工装出入库单_通知记录 created';
END
ELSE
BEGIN
    PRINT 'Step 3.4: View 工装出入库单_通知记录 already exists, skipping...';
END

-- 3.5 位置表视图
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = N'工装出入库单_位置')
BEGIN
    EXEC('CREATE VIEW 工装出入库单_位置 AS SELECT * FROM tool_io_location');
    PRINT 'Step 3.5: View 工装出入库单_位置 created';
END
ELSE
BEGIN
    PRINT 'Step 3.5: View 工装出入库单_位置 already exists, skipping...';
END

-- 3.6 运输异常记录视图
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = N'工装运输异常记录')
BEGIN
    EXEC('CREATE VIEW 工装运输异常记录 AS SELECT * FROM tool_io_transport_issue');
    PRINT 'Step 3.6: View 工装运输异常记录 created';
END
ELSE
BEGIN
    PRINT 'Step 3.6: View 工装运输异常记录 already exists, skipping...';
END


-- ============================================================
-- 步骤4：验证数据一致性
-- ============================================================
DECLARE @old_count INT, @new_count INT;

-- 验证主表
SELECT @old_count = COUNT(*) FROM 工装出入库单_主表;
SELECT @new_count = COUNT(*) FROM tool_io_order;
IF @old_count <> @new_count
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR('Data count mismatch for tool_io_order: old=%d, new=%d', 16, 1, @old_count, @new_count);
END
PRINT 'Step 4: Data consistency verified for tool_io_order (' + CAST(@new_count AS VARCHAR) + ' rows)';

-- 验证明细表
SELECT @old_count = COUNT(*) FROM 工装出入库单_明细;
SELECT @new_count = COUNT(*) FROM tool_io_order_item;
IF @old_count <> @new_count
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR('Data count mismatch for tool_io_order_item: old=%d, new=%d', 16, 1, @old_count, @new_count);
END
PRINT 'Step 4: Data consistency verified for tool_io_order_item (' + CAST(@new_count AS VARCHAR) + ' rows)';

-- 验证操作日志表
SELECT @old_count = COUNT(*) FROM 工装出入库单_操作日志;
SELECT @new_count = COUNT(*) FROM tool_io_operation_log;
IF @old_count <> @new_count
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR('Data count mismatch for tool_io_operation_log: old=%d, new=%d', 16, 1, @old_count, @new_count);
END
PRINT 'Step 4: Data consistency verified for tool_io_operation_log (' + CAST(@new_count AS VARCHAR) + ' rows)';

-- 验证通知记录表
SELECT @old_count = COUNT(*) FROM 工装出入库单_通知记录;
SELECT @new_count = COUNT(*) FROM tool_io_notification;
IF @old_count <> @new_count
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR('Data count mismatch for tool_io_notification: old=%d, new=%d', 16, 1, @old_count, @new_count);
END
PRINT 'Step 4: Data consistency verified for tool_io_notification (' + CAST(@new_count AS VARCHAR) + ' rows)';

-- 验证位置表
SELECT @old_count = COUNT(*) FROM 工装出入库单_位置;
SELECT @new_count = COUNT(*) FROM tool_io_location;
IF @old_count <> @new_count
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR('Data count mismatch for tool_io_location: old=%d, new=%d', 16, 1, @old_count, @new_count);
END
PRINT 'Step 4: Data consistency verified for tool_io_location (' + CAST(@new_count AS VARCHAR) + ' rows)';

-- 验证运输异常记录表
SELECT @old_count = COUNT(*) FROM 工装运输异常记录;
SELECT @new_count = COUNT(*) FROM tool_io_transport_issue;
IF @old_count <> @new_count
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR('Data count mismatch for tool_io_transport_issue: old=%d, new=%d', 16, 1, @old_count, @new_count);
END
PRINT 'Step 4: Data consistency verified for tool_io_transport_issue (' + CAST(@new_count AS VARCHAR) + ' rows)';


-- ============================================================
-- 步骤5：删除旧表（确认无误后执行）
-- ============================================================
-- 注意：此步骤在验证无误后手动执行，或取消注释
/*
DROP TABLE 工装出入库单_主表;
DROP TABLE 工装出入库单_明细;
DROP TABLE 工装出入库单_操作日志;
DROP TABLE 工装出入库单_通知记录;
DROP TABLE 工装出入库单_位置;
DROP TABLE 工装运输异常记录;
*/

COMMIT TRANSACTION;

PRINT '';
PRINT '========================================';
PRINT 'Migration completed successfully!';
PRINT 'Please verify data and then drop old tables manually.';
PRINT '========================================';
