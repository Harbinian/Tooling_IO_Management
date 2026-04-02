# 提示词：实现功能开关（Feature Flag）框架

Primary Executor: Claude Code
Task Type: Refactoring
Priority: P1
Stage: 20112
Goal: Implement a centralized feature flag framework using sys_system_config table
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
当前系统功能开关分散（如 `FEISHU_NOTIFICATION_ENABLED` 在 `config/settings.py` 中），缺乏统一管理机制。新功能 MPL（工装可拆卸件清单）需要管理员可通过 UI 动态开关功能，但现有架构不支持。

### 目标用户
系统管理员

### 核心痛点
- 功能开关硬编码在配置文件中，无法运行时调整
- 新功能需要修改代码才能开关
- 缺乏功能开关的审计日志

### 业务目标
基于已有的 `sys_system_config` 表，实现集中的功能开关框架，支持：
1. 运行时动态开关功能
2. 按角色/组织过滤功能可用性
3. 功能开关变更的操作日志

---

## Required References / 必需参考

- `backend/database/repositories/system_config_repository.py` - 已有配置仓库
- `backend/services/tool_io_service.py` - MPL 功能开关参考
- `backend/database/schema/column_names.py` - 字段名常量
- `docs/ARCHITECTURE.md` - 系统架构文档
- `.claude/rules/00_core.md` - 核心开发规则
- `.claude/rules/01_workflow.md` - ADP 四阶段开发协议

---

## Core Task / 核心任务

### 架构重构目标

1. **建立 FeatureFlagService**
   - 位置：`backend/services/feature_flag_service.py`
   - 职责：统一管理功能开关的读取、缓存、变更通知

2. **扩展 sys_system_config 表用途**
   - 现有表结构支持 `config_key`、`config_value`、`config_type` 等字段
   - 新增功能开关元数据：开关类型、影响的API端点、默认状态

3. **迁移现有开关**
   - 将 `FEISHU_NOTIFICATION_ENABLED` 从 `config/settings.py` 迁移到数据库
   - 其他硬编码开关同理

4. **API 端点**
   - `GET /api/admin/feature-flags` - 获取所有功能开关
   - `PUT /api/admin/feature-flags/{flag_key}` - 更新开关状态
   - `GET /api/feature-flags/{flag_key}/enabled` - 检查开关状态（供内部服务调用）

5. **前端集成**
   - 在 `SettingsPage.vue` 中添加功能开关管理 UI
   - 使用现有 `systemConfig.js` API 封装

---

## Required Work / 必需工作

### Phase 1: PRD - 业务需求确认
- [ ] 定义功能开关的数据模型（key、value、type、description、affected_endpoints）
- [ ] 确定需要迁移的现有硬编码开关
- [ ] 定义开关变更的审计日志格式

### Phase 2: Data - 数据 Schema 审视
- [ ] 检查 `sys_system_config` 表结构是否满足需求
- [ ] 确认无需新建表
- [ ] 设计功能开关的元数据结构（可复用现有字段或扩展）

### Phase 3: Architecture - 架构设计
- [ ] 设计 `FeatureFlagService` 接口：
  - `is_enabled(flag_key: str, context: Dict) -> bool`
  - `get_all_flags() -> List[Dict]`
  - `set_flag(flag_key: str, value: Any, operator: str) -> None`
- [ ] 设计缓存策略（TTL + 变更通知）
- [ ] 设计向后兼容方案（config/settings.py 中的默认值作为兜底）

### Phase 4: Execution - 精确执行

#### Step 1: 创建 FeatureFlagService
```python
# backend/services/feature_flag_service.py
class FeatureFlagService:
    def __init__(self, cache_ttl_seconds: int = 60):
        self._repo = SystemConfigRepository()
        self._cache: Dict[str, Tuple[bool, datetime]] = {}
        self._cache_ttl = cache_ttl_seconds

    def is_enabled(self, flag_key: str) -> bool:
        """Check if a feature flag is enabled."""

    def get_all_flags(self) -> List[Dict]:
        """Get all feature flags with metadata."""

    def set_flag(self, flag_key: str, value: Any, operator_id: str) -> None:
        """Update a feature flag value."""
```

#### Step 2: 迁移 FEISHU_NOTIFICATION_ENABLED
- 保留 `config/settings.py` 中的默认值作为兜底
- 运行时优先读取数据库值

#### Step 3: 实现 API 路由
- 在 `backend/routes/system_config_routes.py` 添加功能开关端点

#### Step 4: 前端 UI
- 在 `frontend/src/pages/settings/SettingsPage.vue` 添加开关管理表格
- 使用 `el-switch` 组件

#### Step 5: 验证
- 切换功能开关并验证行为变化
- 确认开关变更被正确记录

---

## Constraints / 约束条件

1. **向后兼容**：现有 `FEISHU_NOTIFICATION_ENABLED` 配置必须继续工作
2. **事务处理**：开关更新必须记录操作日志
3. **零退化**：不得破坏现有 MPL 功能和飞书通知功能
4. **代码规范**：使用英文变量名、`snake_case`、4空格缩进
5. **文档权威性**：如架构有重大变更，更新 `docs/ARCHITECTURE.md`

---

## Completion Criteria / 完成标准

1. [ ] `FeatureFlagService` 实现并通过语法检查
2. [ ] `FEISHU_NOTIFICATION_ENABLED` 成功迁移到数据库开关
3. [ ] API 端点 `/api/admin/feature-flags/*` 注册成功
4. [ ] 前端开关管理 UI 在 SettingsPage 中可用
5. [ ] 开关变更产生正确的操作日志
6. [ ] 后端语法检查通过：`python -m py_compile backend/services/feature_flag_service.py backend/routes/system_config_routes.py`
7. [ ] 前端构建成功：`cd frontend && npm run build`
8. [ ] 文档 `docs/ARCHITECTURE.md` 更新（如需要）
