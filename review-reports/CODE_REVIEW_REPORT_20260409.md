# 全库代码审查报告 / Code Review Report

- **审查日期**: 2026-04-09
- **审查范围**: backend / frontend / 根目录 Python 入口与配置
- **审查方式**: 规则扫描 + 关键文件抽样 + 语法/单测冒烟

---

## 1) 执行摘要

本轮审查结论：

1. **架构分层整体清晰**（route → service → repository → db），主流程代码组织可维护。
2. 仍存在**规则一致性问题**，主要集中在：
   - 配置读取未完全收敛到 `config/settings.py`
   - SQL 字段/表常量规范执行不一致
   - 前端主题色变量规范执行不一致（硬编码颜色）
3. 基础质量检查通过（关键 Python 文件语法通过、基础单测可运行），但需要补一轮“规范性”修复。

---

## 2) 关键发现（按优先级）

### P1-1 配置读取分散，绕过统一 settings 入口

**现象**
- `DatabaseManager` 在已引入 `settings` 的情况下仍大量 `os.getenv(...)` 回退读取。 
- `utils/feishu_api.py` 直接在类初始化中读取 `os.getenv(...)`。

**证据**
- `backend/database/core/database_manager.py` 第 56-73 行。 
- `utils/feishu_api.py` 第 21-23、102 行。

**风险**
- 配置来源分裂，测试环境/生产环境行为不一致。
- 未来做配置审计或密钥轮换时容易漏改。

**建议**
- 在 `DatabaseManager` 与 `FeishuBase` 中统一消费 `config.settings.settings`。
- 将 `os.getenv` 仅保留在 `config/settings.py`。

---

### P1-2 SQL 常量规范执行不一致（存在直接中文表名）

**现象**
- `batch_query_tools` 中直接使用 `FROM 工装主数据`，未通过 schema 常量统一管理。

**证据**
- `backend/services/order_query_service.py` 第 136 行。

**风险**
- Schema 演进时改名/映射变更难以全局追踪。
- 与 `column_names.py` 的单一来源原则冲突。

**建议**
- 使用 `backend/database/schema/column_names.py` 中的表名/字段常量替代直写。

---

### P2-1 前端存在多处硬编码语义色，主题一致性风险

**现象**
- 页面中仍使用 `text-emerald-400`、`bg-emerald-500/10` 等硬编码色值。

**证据（抽样）**
- `frontend/src/pages/HomePage.vue` 第 129、135 行。

**风险**
- 暗黑模式与品牌主题切换时出现对比度/语义色不一致。

**建议**
- 用语义化 token（如 `text-primary-foreground`、`bg-primary/10` 或统一 CSS 变量）替代硬编码色。

---

## 3) 正向观察（Good Practices）

1. `config/settings.py` 已实现生产环境 `SECRET_KEY` 强制校验与开发环境临时 key 生成，安全基线优于固定默认密钥。 
2. `DatabaseManager.execute_query` 对事务回滚、游标关闭和错误日志具备基础防护。 
3. 仓库已有较完整测试资产，`tests/` 目录覆盖服务层和路由相关能力。

---

## 4) 本次执行的检查

1. Python 语法检查：
   - `python -m py_compile web_server.py database.py backend/services/tool_io_service.py config/settings.py utils/feishu_api.py`
2. 单测冒烟：
   - `pytest -q tests/test_api_response_helpers.py`（首次因 `PYTHONPATH` 未设置失败）
   - `PYTHONPATH=. pytest -q tests/test_api_response_helpers.py`（通过）
3. 规则扫描（抽样自动化）：
   - `os.getenv` 使用点
   - 中文 SQL 直写点
   - 前端硬编码语义色点

---

## 5) 建议的后续动作

1. **优先修复（P1）**：配置入口统一 + SQL 常量化。
2. **并行修复（P2）**：前端颜色 token 收敛，补一次 UI 回归检查。
3. 在后续修复 PR 中补充对应回归测试（配置注入路径、工具批量查询 SQL 常量依赖、主题切换快照/可视校验）。

