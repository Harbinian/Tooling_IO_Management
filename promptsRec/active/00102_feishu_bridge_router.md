# 飞书桥接服务 - 消息路由与去重

---

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P0
Stage: 00102
Goal: 实现消息路由和去重机制，支持 /status、/help、/claude 等指令
Dependencies: 00101
Execution: RUNPROMPT

---

## Context

**需求背景**:
在 WebSocket 客户端基础上，需要解析飞书消息，识别指令类型，路由到对应处理器。同时需要去重，避免重复处理同一消息。

**本阶段目标**:
- 实现 MessageRouter 模块
- 支持 /status、/help、/claude 指令解析
- 实现消息去重机制

---

## Phase 1: PRD - 业务需求分析

**业务场景**:
用户通过飞书发送指令，服务解析指令内容，路由到不同处理器。

**目标用户**:
- 开发者本人

**核心痛点**:
- 没有指令解析，无法响应用户命令

**业务目标**:
- 指令解析准确
- 消息去重有效

---

## Phase 2: Data - 数据流转

**消息处理流程**:
```
FeishuWebSocketClient → MessageRouter → 去重检查 → 指令解析 → 处理器
```

**支持指令**:
| 指令 | 格式 | 处理器 | 返回内容 |
|------|------|--------|---------|
| status | `/status` | 内置 | 服务运行状态 |
| help | `/help` | 内置 | 帮助信息 |
| claude | `/claude <command>` | CLIExecutor | Claude CLI 执行结果 |

---

## Phase 3: Architecture - 架构设计

**模块位置**: `feishu-bridge/feishu_bridge/router.py`

**类定义**:

```python
class MessageRouter:
    """消息路由器"""

    def __init__(self):
        """初始化路由器"""

    def route(self, message: dict) -> RoutingResult:
        """
        路由消息
        返回: RoutingResult(instruction, args, sender)
        """

    def register_handler(self, instruction: str, handler: Callable):
        """注册指令处理器"""
```

**消息去重**:

```python
class MessageDeduplicator:
    """消息去重器"""

    def __init__(self, window_size: int = 100):
        """滑动窗口大小"""

    def is_duplicate(self, message_id: str) -> bool:
        """检查是否重复"""

    def add(self, message_id: str):
        """添加消息 ID"""
```

**接口契约**:
- `route()` 返回的消息格式:
  ```python
  class RoutingResult:
      instruction: str      # "status" | "help" | "claude"
      args: str            # 指令参数（如 "echo hello"）
      sender: dict         # 发送者信息
      message_id: str      # 消息 ID
  ```

**去重规则**:
- 内存维护最近 100 条 message_id 的集合
- 收到消息先检查是否已处理
- 重复消息直接返回 None，不触发处理器

---

## Phase 4: Execution - 精确执行

### 4.1 创建路由器模块

**文件**: `feishu-bridge/feishu_bridge/router.py`

**实现要点**:
- MessageDeduplicator: 维护滑动窗口集合
- MessageRouter: 解析指令，注册处理器
- 指令格式: `/<instruction> <args>` 或直接 `/<instruction>`

### 4.2 内置指令处理器

**/status 处理器**:
```python
def handle_status() -> str:
    return "Feishu Bridge is running"
```

**/help 处理器**:
```python
def handle_help() -> str:
    return """Available commands:
/status - Show service status
/help - Show this help message
/claude <command> - Execute Claude CLI command"""
```

### 4.3 更新 main.py 集成路由器

**修改**:
- 创建 MessageRouter 实例
- 注册 /status、/help 处理器
- 在客户端消息回调中调用 router.route()

### 4.4 日志规范

**去重日志**:
```python
logger.debug(f"Duplicate message detected: {message_id}")
```

**路由日志**:
```python
logger.info(f"Routing message: instruction={instruction}, args={args}")
```

---

## Constraints

1. **不写具体代码** - 只描述架构和接口契约
2. **去重是内存实现** - 不使用数据库
3. **处理器可扩展** - 支持注册新的指令处理器
4. **异常不阻塞** - 解析异常要捕获，不影响后续消息处理

---

## Completion Criteria

1. [ ] `/status` 指令返回服务状态
2. [ ] `/help` 指令返回帮助信息
3. [ ] `/claude` 指令解析出 command 参数
4. [ ] 重复发送同一 message_id 的消息只处理一次
5. [ ] 路由器模块可通过 `python -c "from feishu_bridge.router import MessageRouter"` 导入
