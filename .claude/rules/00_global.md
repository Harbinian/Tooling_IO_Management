# 全局开发规则 / Global Development Rules

---

## 编码 / Encoding

所有生成的文件必须使用 UTF-8 (无 BOM) 编码。 / All generated files must use UTF-8 (without BOM) encoding.

Python 示例: / Python example:
```python
open(path, encoding="utf-8")
```

中文乱码特征字符（检测到立即报警）:
- `鍒涘缓` (应为"创建")
- `宸ヨ` (应为"工装")
- `鎼滅储` (应为"搜索")
- `鍗曟` (应为"单据")

---

## 字段名常量使用规范 / Field Name Constant Usage

**所有 SQL 查询中的中文字段名必须使用 `backend/database/schema/column_names.py` 中定义的常量。**

### 正确用法:

```python
from backend.database.schema.column_names import ORDER_COLUMNS

sql = f"SELECT {ORDER_COLUMNS['order_no']} FROM 工装出入库单_主表"
```

### 禁止用法:

```python
# 禁止直接使用中文字段名字面量
sql = "SELECT 出入库单号 FROM 工装出入库单_主表"

# 禁止使用 Unicode 转义
sql = "SELECT \u51fa\u5165\u5e93\u5355\u53f7 FROM 工装出入库单_主表"
```

### 理由:

- 防止复制粘贴时产生乱码
- 便于全局搜索和修改
- 确保所有 SQL 语句使用一致的字段名

---

## 外部系统表访问规范 / External System Table Access Rules

**本项目必须严格遵守以下规则，绝不允许直接修改外部系统表结构。**

### 已识别的外部系统表 / Known External Tables

| 表名 | 用途 | 管理方 | 访问方式 |
|------|------|--------|----------|
| `工装身份卡_主表` | 工装主数据（序列号、图号、状态等） | **外部系统**，禁止修改 Schema | 只读查询 + 特定字段更新 |

### 访问规则 / Access Rules

1. **禁止 DDL 操作**: 严禁对外部系统表执行 `CREATE TABLE`、`ALTER TABLE`、`DROP TABLE`
2. **只读优先**: 外部系统表只做 SELECT 查询，不做结构变更
3. **字段更新需通过常量**: 对外部系统表的字段更新必须通过 `column_names.py` 中的常量引用
4. **禁止修改 Schema**: 严禁添加、删除、修改外部系统表的字段定义

### 正确用法:

```python
from backend.database.schema.column_names import TOOL_MASTER_COLUMNS

# 正确：通过常量引用外部表字段
sql = f"UPDATE [{TOOL_MASTER_TABLE}] SET [{TOOL_MASTER_COLUMNS['io_status']}] = ? WHERE [{TOOL_MASTER_COLUMNS['tool_code']}] = ?"

# 正确：使用常量进行 SELECT
sql = f"SELECT [{TOOL_MASTER_COLUMNS['tool_code']}] FROM [{TOOL_MASTER_TABLE}]"
```

### 禁止用法:

```python
# 禁止直接使用中文字段名字面量（即使能工作）
sql = "UPDATE [工装身份卡_主表] SET [出入库状态] = ? WHERE [序列号] = ?"

# 禁止硬编码字段名
sql = f"UPDATE [{TOOL_MASTER_TABLE}] SET [库位] = ? WHERE [序列号] = ?"
```

### 理由:

- 外部系统表由其他系统管理，其 Schema 可能随时变化
- 通过常量引用可以在 Schema 变更时只需修改一处
- 便于识别项目中所有对外部系统表的访问点

### 新增外部表时的处理:

1. 在 `column_names.py` 中创建新的 `*_CHINESE_COLUMNS` 常量（键名和值都是中文字段名）
2. 在 `TOOL_MASTER_TABLE` 等常量中定义表名
3. 所有 SQL 必须通过常量引用字段和表名
4. 在本规则文件的"已识别的外部系统表"章节中添加记录

---

## 语言标准 / Language Standard

代码、注释、变量名、提交信息必须使用英文。 / Code, comments, variable names, commit messages must be in English.

文档可以使用中文或中英双语。 / Documentation can be Chinese or bilingual.

### AI CLI 交互界面输出 / AI CLI Interaction Output

Claude Code、Codex、Gemini 等 AI 代理的 CLI 交互界面使用中文输出。/ Claude Code, Codex, Gemini and other AI agent CLI interaction interfaces output in Chinese.

与 AI 代理进行文字交谈时，使用中文或中英双语。/ When communicating with AI agents via text, use Chinese or bilingual Chinese-English.

仅在代码、API、数据库、配置文件等场合使用英文。/ Use English only in code, APIs, database, configuration files and other technical contexts.

---

## 代码完整性 / Code Integrity

AI 严禁生成占位符代码，例如： / The AI must never produce placeholder code such as:

```
...
// insert code here
TODO
```

所有代码必须完整且可执行。 / All code must be complete and executable.

---

## 命名规则 / Naming Rules

变量和函数禁止使用拼音。 / Variables and functions must not use Pinyin.

使用清晰的英文名称。 / Use clear English names.

示例: / Example:
```python
toolInventory
toolLocation
```

---

## 错误处理 / Error Handling

关键 I/O 或网络操作必须使用 try-except 块保护。 / Critical I/O or network operations must be protected with try-except blocks.

---

## Git 规范 / Git Discipline

每个重大功能必须对应一个 Git 提交。 / Every major feature must correspond to a Git commit.

示例: / Example:
```
feat: add tool_io_order schema
feat: implement order submission API
fix: correct tool reservation logic
```

---

## 文档权威性 / Documentation Source of Truth

### 必须参考的权威文档 / Mandatory Reference Documents

以下文件是开发的唯一权威来源，代码实现必须遵循：

| 文档 | 用途 | 更新时机 |
|------|------|----------|
| docs/PRD.md | 产品需求定义 | 功能变更前必须同步 |
| docs/ARCHITECTURE.md | 系统架构和技术选型 | 架构变更前必须同步 |
| docs/API_SPEC.md | API 接口规范 | API 变更前必须同步 |
| docs/DB_SCHEMA.md | 数据库表结构 | Schema 变更前必须同步 |
| docs/RBAC_DESIGN.md | RBAC 权限模型设计 | 权限变更前必须同步 |
| docs/RBAC_PERMISSION_MATRIX.md | 权限矩阵 | 权限变更前必须同步 |
| docs/RBAC_INIT_DATA.md | RBAC 初始数据 | 角色/权限数据变更必须同步 |
| backend/database/schema/column_names.py | 中文字段名常量 | 字段变更必须同步 |

### 文档更新规则 / Document Update Rules

1. **先文档后代码**: 代码实现前必须先更新相关文档
2. **同步更新**: 功能变更时立即更新 docs/PRD.md
3. **同步更新**: API 变更时立即更新 docs/API_SPEC.md
4. **同步更新**: 权限变更时立即更新 RBAC 文档
5. **禁止绕过**: 严禁在文档更新前进行代码实现

### 任务完成时的文档维护 / Documentation Maintenance on Task Completion

执行任务完成后，检查并更新（如有必要）以下内容：

| 任务类型 | 必须检查的文档 |
|----------|---------------|
| 功能任务 | PRD.md, API_SPEC.md, ARCHITECTURE.md |
| Bug 修复 | 相关功能文档 |
| 重构任务 | ARCHITECTURE.md, DB_SCHEMA.md |
| 权限任务 | RBAC_DESIGN.md, RBAC_PERMISSION_MATRIX.md |

如任务导致文档与实现不一致，立即更新文档。

### 禁止行为 / Forbidden Actions

- 严禁在文档更新前进行代码实现
- 严禁跳过文档更新直接提交代码
- 严禁使文档与实现不一致

---

## 业务规则 / Business Rule

所有仓库操作必须可追溯。 / All warehouse operations must be traceable.

每个操作必须记录： / Every action must record:

- 操作人 / operator
- 时间戳 / timestamp
- 订单ID / order_id
- 之前状态 / previous_state
- 下一状态 / next_state

---

## UI 一致性规则 / UI Consistency Rules

所有关键操作（提交、取消、确认、删除）必须在涉及该操作的每个页面保持一致的确认行为。/ All critical operations (submit, cancel, confirm, delete) must maintain consistent confirmation behavior across all pages that involve that operation.

**确认对话框要求 / Confirmation Dialog Requirements**:

| 操作 | 必需页面 | 确认消息格式 |
|------|---------|------------|
| 提交 / Submit | OrderList.vue, OrderDetail.vue | `确认提交单据 ${orderNo} 吗？提交后将进入保管员审核流程。` |
| 取消 / Cancel | OrderDetail.vue | `确认取消单据 ${orderNo} 吗？` |
| 最终确认 / Final Confirm | OrderDetail.vue | `确认最终完成单据 ${orderNo} 吗？` |
| 删除 / Delete | OrderDetail.vue | `确认删除单据 ${orderNo} 吗？删除后不可恢复。` |

**禁止行为 / Forbidden Actions**:

- 严禁在同一操作的不同页面使用不同的确认对话框样式
- 严禁省略关键操作的确认步骤
- 严禁使用硬编码颜色值，必须使用 CSS 变量
