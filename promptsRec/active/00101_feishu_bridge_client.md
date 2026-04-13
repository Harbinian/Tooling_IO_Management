# 飞书桥接服务 - 飞书 WebSocket 客户端

---

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P0
Stage: 00101
Goal: 实现飞书 WebSocket 客户端，与飞书服务器建立长连接
Dependencies: 00100
Execution: RUNPROMPT

---

## Context

**需求背景**:
飞书桥接服务需要与飞书服务器建立 WebSocket 长连接，接收用户消息。本阶段在骨架基础上实现客户端模块。

**本阶段目标**:
- 实现 FeishuWebSocketClient 模块
- 与飞书服务器建立长连接
- 处理连接状态变化和消息接收

---

## Phase 1: PRD - 业务需求分析

**业务场景**:
服务启动后，自动与飞书服务器建立 WebSocket 长连接，保持连接活跃，接收用户发送的消息。

**目标用户**:
- 开发者本人

**核心痛点**:
- 没有 WebSocket 客户端，无法接收飞书消息

**业务目标**:
- 长连接稳定建立
- 连接状态可观察（日志）
- 支持断线重连

---

## Phase 2: Data - 数据流转

**消息接收流程**:
```
飞书服务器 → WebSocket → FeishuWebSocketClient → 回调处理
```

**连接状态**:
| 状态 | 触发条件 | 日志输出 |
|------|---------|---------|
| connecting | 正在连接 | "Connecting to Feishu..." |
| connected | 连接成功 | "Connected to Feishu" |
| reconnecting | 断线重连 | "Reconnecting to Feishu..." |
| disconnected | 连接断开 | "Disconnected from Feishu" |
| error | 连接错误 | "Feishu connection error: {detail}" |

---

## Phase 3: Architecture - 架构设计

**模块位置**: `feishu-bridge/feishu_bridge/client.py`

**类定义**:

```python
class FeishuWebSocketClient:
    """飞书 WebSocket 客户端"""

    def __init__(self, app_id: str, app_secret: str):
        """初始化客户端"""

    def connect(self):
        """建立 WebSocket 连接"""

    def disconnect(self):
        """断开连接"""

    def on_message(self, callback: Callable[[dict], None]):
        """注册消息回调，接收原始消息字典"""

    def on_connect(self, callback: Callable[[], None]):
        """注册连接成功回调"""

    def on_disconnect(self, callback: Callable[[], None]):
        """注册断开连接回调"""

    def run_forever(self):
        """主循环，保持连接，处理事件"""
```

**接口契约**:
- `on_message` 回调接收的消息格式:
  ```python
  {
      "message_id": str,      # 消息唯一 ID
      "chat_id": str,         # 会话 ID
      "sender": {             # 发送者信息
          "user_id": str,
          "name": str
      },
      "content": str,         # 消息内容（原始文本）
      "create_time": str      # 创建时间
  }
  ```

**技术选型**:
- 使用 `lark-oapi` SDK 的 WebSocket 模式
- 具体 API 参考: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python-sdk/websocket-overview

---

## Phase 4: Execution - 精确执行

### 4.1 创建客户端模块

**文件**: `feishu-bridge/feishu_bridge/client.py`

**实现要点**:
- 导入 lark-oapi SDK
- 使用 SDK 提供的 WebSocket 客户端
- 实现连接、断开、消息处理逻辑
- 日志记录连接状态变化

### 4.2 更新 main.py 集成客户端

**修改**:
- 在 `run` 命令中加载配置
- 创建 FeishuWebSocketClient 实例
- 注册消息回调（暂时只打印日志）
- 调用 `run_forever()`

### 4.3 日志规范

**连接状态日志**:
```python
from loguru import logger

logger.info("Connecting to Feishu WebSocket...")
logger.info("Connected to Feishu")
logger.warning("Reconnecting to Feishu...")
logger.error("Feishu connection error: {detail}")
logger.info("Disconnected from Feishu")
```

**消息接收日志**:
```python
logger.debug(f"Received message: {message_id} from {user_id}")
```

---

## Constraints

1. **不写具体代码** - 只描述架构和接口契约
2. **使用官方 SDK** - 通过 lark-oapi SDK 连接飞书，不自己实现 WebSocket
3. **日志可观察** - 所有关键状态变化都要有日志
4. **异常不崩溃** - 连接错误要捕获并记录，不导致程序崩溃

---

## Completion Criteria

1. [ ] `feishu-bridge run` 启动后日志显示 "Connecting to Feishu..."
2. [ ] 连接成功日志显示 "Connected to Feishu"
3. [ ] 收到飞书消息后日志记录 message_id
4. [ ] 连接断开后日志显示 "Disconnected" 或 "Reconnecting"
5. [ ] 客户端模块可通过 `python -c "from feishu_bridge.client import FeishuWebSocketClient"` 导入
