# 全局开发规则 / Global Development Rules

---

## 编码 / Encoding

所有生成的文件必须使用 UTF-8 编码。 / All generated files must use UTF-8 encoding.

Python 示例: / Python example:
```python
open(path, encoding="utf-8")
```

---

## 语言标准 / Language Standard

代码、注释、变量名、提交信息必须使用英文。 / Code, comments, variable names, commit messages must be in English.

文档可以使用中文或中英双语。 / Documentation can be Chinese or bilingual.

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

以下文件是权威来源： / The following files are the authoritative source:

- docs/PRD.md - 产品需求文档
- docs/ARCHITECTURE.md - 架构文档
- docs/API_SPEC.md - API 规范
- docs/DB_SCHEMA.md - 数据库 Schema

代码不得偏离这些文档，必须先更新文档再修改代码。 / Code must not deviate from these documents without updating them first.

---

## 业务规则 / Business Rule

所有仓库操作必须可追溯。 / All warehouse operations must be traceable.

每个操作必须记录： / Every action must record:

- 操作人 / operator
- 时间戳 / timestamp
- 订单ID / order_id
- 之前状态 / previous_state
- 下一状态 / next_state
