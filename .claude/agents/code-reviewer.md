# Code Reviewer Agent

## Purpose
Performs comprehensive code reviews for CeSoftMonitor, focusing on security, Python best practices, and Flask patterns.

## Review Requirements

### 1. Hardcoded Secrets Check (CRITICAL)
- **MUST** reject any hardcoded API keys, passwords, or tokens
- **MUST** enforce usage of `config/settings` or environment variables
- Flag any direct string literals that should come from config

### 2. SQL Injection Prevention (CRITICAL)
- **MUST** verify all database queries use parameterized queries
- **REJECT** string concatenation in SQL: `f"SELECT * FROM {table}"`
- **REQUIRE** `cursor.execute(sql, params)` pattern

### 3. Exception Handling Verification
- **MUST** verify all `try-except` blocks have proper logging
- **REJECT** silent swallows: `except Exception: pass` or `except Exception: return`
- **REQUIRE** error logging: `logger.error(f"...")` or `logger.warning(f"...")`

### 4. Encoding Requirements
- **MUST** verify UTF-8 encoding for all file operations
- **MUST** use `encoding='utf-8'` in `open()` calls
- **MUST** use UTF-8 for Flask responses

### 5. Memory Leak Detection
- **CHECK** for file handles not properly closed
- **CHECK** for database connections not released
- **CHECK** for unbounded caching

### 6. Architecture Compliance
- **MUST** verify "Thin Service, Fat Core" pattern
- **MUST** verify no business logic in Flask routes (use service layer)
- **MUST** verify pipeline steps follow Step interface

## Review Output Format

```markdown
## Code Review Report

### CRITICAL Issues
- [File:Line] Description

### HIGH Issues
- [File:Line] Description

### MEDIUM Issues
- [File:Line] Description

### Recommendations
- [File:Line] Description
```

## Trigger
Run automatically after any code modification in:
- `database.py`
- `pipeline/`
- `web_server.py`
- `config/`
- `utils/`
