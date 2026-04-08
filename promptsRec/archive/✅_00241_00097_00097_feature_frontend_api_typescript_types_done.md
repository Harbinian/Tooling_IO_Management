---
name: 00097_feature_frontend_api_typescript_types
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/01_workflow.md
  - .claude/rules/04_frontend.md
version: 1.0.0
---

# 00097: 功能开发 - 前端 API 层 TypeScript 类型定义

## Header / 头部信息

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00097
Goal: 为前端 API 层添加 TypeScript 类型定义，提升类型安全性
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

架构评审发现前端 API 层存在以下问题：

1. **无 TypeScript 类型定义**：所有 API 返回 `any`，无法在编译期发现类型错误
2. **错误类型单一**：只有 `ElMessage.error`，无区分业务错误（400）与系统错误（500）
3. **API 封装层已有**：存在 `frontend/src/api/*.js` 封装，可作为类型定义基础

**业务价值**：
- 编译期发现类型错误，减少运行时 bug
- 改善开发体验（IDE 自动补全、类型提示）
- 统一前后端接口契约

---

## Phase 1 - PRD / 业务需求分析

**业务背景**：
- 前端 `frontend/src/api/` 包含 14 个 API 模块
- 后端 API 返回格式已基本稳定（成功 `{"success": true, "data": ...}`，错误 `{"success": false, "error": ...}`）
- 当前使用 JavaScript，无类型约束

**目标用户**：
- 前端开发者（更好的开发体验）
- 维护者（更容易理解 API 契约）

**核心功能**：
1. 定义统一响应类型 `ApiResponse<T>`
2. 为主要 API 模块添加类型定义
3. 区分业务错误类型与系统错误类型

**成功标准**：
- 主要 API 模块有完整类型定义
- 编译无类型错误
- 改善开发体验

---

## Phase 2 - Data / 数据流转审视

**现有 API 文件**：

| 文件 | 用途 | 类型需求 |
|------|------|---------|
| `frontend/src/api/client.js` | Axios 封装，通用拦截器 | 核心，需先定义 |
| `frontend/src/api/orders.js` | 订单 API | 高优先级 |
| `frontend/src/api/tools.js` | 工装搜索 API | 高优先级 |
| `frontend/src/api/mpl.js` | MPL API | 中优先级 |
| `frontend/src/api/auth.js` | 认证 API | 中优先级 |
| `frontend/src/api/dashboard.js` | 仪表盘 API | 中优先级 |

**目标类型结构**：

```typescript
// 统一响应格式
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

// 分页响应
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// 订单类型
interface Order {
  order_no: string;
  order_type: 'inbound' | 'outbound';
  status: string;
  // ... 其他字段
}

// 错误类型
type ApiError = {
  code: string;
  message: string;
};
```

---

## Phase 3 - Architecture / 架构设计

### 方案设计

**方案：创建 TypeScript 类型定义文件**

```
frontend/src/api/types/
├── response.ts      # 统一响应类型
├── order.ts         # 订单相关类型
├── tool.ts          # 工装相关类型
├── mpl.ts           # MPL 相关类型
└── index.ts        # 导出所有类型
```

**实施策略**：
1. 先定义 `response.ts` 中的基础类型
2. 逐步为各 API 模块添加类型
3. 使用 `// @ts-check` 或迁移到 `.ts` 文件

**风险识别**：
- 后端 API 字段可能变化
- 类型定义与实际 API 不一致

---

## Phase 4 - Execution / 精确执行

### 执行步骤

**Step 1**: 分析后端 API 响应格式
```
- 读取 docs/API_SPEC.md 了解 API 规范
- 抽查几个后端路由的响应格式
- 确认成功/错误响应结构
```

**Step 2**: 创建类型定义文件
```
- 创建 frontend/src/api/types/response.ts
- 定义 ApiResponse, PaginatedResponse 等基础类型
```

**Step 3**: 为 orders.js 添加类型
```
- 创建 frontend/src/api/types/order.ts
- 定义 Order, OrderItem, OrderCreateInput 等类型
- 在 orders.js 中导入使用
```

**Step 4**: 为其他 API 模块添加类型
```
- tools.js → types/tool.ts
- mpl.js → types/mpl.ts
- auth.js → types/auth.ts
```

**Step 5**: 验证
```
- 运行 tsc --noEmit 检查类型错误
- 如项目未配置 TypeScript，使用 vscode 内置类型检查
```

**Step 6**: 文档同步
```
- 更新 docs/ARCHITECTURE.md（前端 API 层类型安全说明）
```

---

## Required References / 必需参考

| 文件 | 路径 | 用途 |
|------|------|------|
| API 封装 | `frontend/src/api/client.js` | 了解当前封装结构 |
| 订单 API | `frontend/src/api/orders.js` | 主要类型定义目标 |
| 工装 API | `frontend/src/api/tools.js` | 类型定义目标 |
| API规范 | `docs/API_SPEC.md` | API 字段定义 |
| 前端规范 | `.claude/rules/04_frontend.md` | 前端开发规范 |

---

## Constraints / 约束条件

1. **不修改业务逻辑**：只添加类型，不改变运行时行为
2. **向后兼容**：JavaScript 文件逐步迁移，不强制要求全部改为 .ts
3. **类型准确性**：基于实际 API 响应定义，不假设
4. **UTF-8 编码**：所有文件必须 UTF-8 无 BOM

---

## Completion Criteria / 完成标准

- [ ] `frontend/src/api/types/response.ts` 已创建，包含 ApiResponse 等基础类型
- [ ] `frontend/src/api/types/order.ts` 已创建，订单相关类型完整
- [ ] orders.js 已导入并使用类型定义
- [ ] 编译无新增类型错误（如项目使用 TypeScript）
- [ ] docs/ARCHITECTURE.md 已更新
- [ ] 前端功能验证通过（类型定义不影响运行时行为）
