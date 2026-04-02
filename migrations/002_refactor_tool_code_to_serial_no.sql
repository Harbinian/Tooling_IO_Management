-- UTF-8
-- Refactor internal tool identifier column name from tool_code to serial_no.
-- External table Tooling_ID_Main keeps its existing Chinese column mapping.

BEGIN TRANSACTION;

IF COL_LENGTH(N'tool_io_order_item', N'serial_no') IS NULL
BEGIN
    ALTER TABLE [tool_io_order_item] ADD [serial_no] VARCHAR(64) NULL;
END

IF COL_LENGTH(N'tool_io_order_item', N'tool_code') IS NOT NULL
BEGIN
    UPDATE [tool_io_order_item]
    SET [serial_no] = [tool_code]
    WHERE [serial_no] IS NULL;
END

IF COL_LENGTH(N'tool_status_change_history', N'serial_no') IS NULL
BEGIN
    ALTER TABLE [tool_status_change_history] ADD [serial_no] NVARCHAR(100) NULL;
END

IF COL_LENGTH(N'tool_status_change_history', N'tool_code') IS NOT NULL
BEGIN
    UPDATE [tool_status_change_history]
    SET [serial_no] = [tool_code]
    WHERE [serial_no] IS NULL;
END

IF EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_tool_io_order_item_tool_code'
      AND object_id = OBJECT_ID(N'tool_io_order_item')
)
BEGIN
    DROP INDEX [IX_tool_io_order_item_tool_code] ON [tool_io_order_item];
END

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_tool_io_order_item_serial_no'
      AND object_id = OBJECT_ID(N'tool_io_order_item')
)
BEGIN
    CREATE INDEX [IX_tool_io_order_item_serial_no] ON [tool_io_order_item]([serial_no]);
END

IF EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_tool_status_change_history_tool_code_time'
      AND object_id = OBJECT_ID(N'tool_status_change_history')
)
BEGIN
    DROP INDEX [IX_tool_status_change_history_tool_code_time] ON [tool_status_change_history];
END

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_tool_status_change_history_serial_no_time'
      AND object_id = OBJECT_ID(N'tool_status_change_history')
)
BEGIN
    CREATE INDEX [IX_tool_status_change_history_serial_no_time]
    ON [tool_status_change_history]([serial_no], [change_time] DESC);
END

COMMIT TRANSACTION;

-- Optional cleanup after application rollout and validation:
-- ALTER TABLE [tool_io_order_item] DROP COLUMN [tool_code];
-- ALTER TABLE [tool_status_change_history] DROP COLUMN [tool_code];
