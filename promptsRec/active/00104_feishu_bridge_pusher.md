# 飞书桥接服务 - 结果推送

---

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P0
Stage: 00104
Goal: 实现结果推送模块，将 CLI 执行结果通过飞书 bot 主动推送
Dependencies: 00101
Execution: RUNPROMPT

---

## Context

**需求背景**:
CLI 执行结果需要通过飞书 bot 主动推送给用户，而不是等待用户轮询。

**本阶段目标**:
- 实现 ResultPusher 模块
- 支持消息卡片格式化
- 支持重试机制

---

## Phase 1: PRD - 业务需求分析

**业务场景**:
CLI 执行完成后，将结果通过飞书 bot 推送到用户会话。

**目标用户**:
- 开发者本人

**核心痛点**:
- 没有推送机制，无法将结果发回飞书

**业务目标**:
- 推送成功
- 失败可重试
- 不阻塞后续消息处理

---

## Phase 2: Data - 数据流转

**推送流程**:
```
ExecutionResult → ResultPusher.format() → 飞书 API → 推送结果
```

**消息卡片格式**:
| 类型 | 样式 | 内容 |
|------|------|------|
| 成功 | 绿色边框 | stdout 输出 |
| 失败 | 红色边框 | 错误信息 |
| 超时 | 黄色边框 | 超时提示 + 已捕获输出 |

---

## Phase 3: Architecture - 架构设计

**模块位置**: `feishu-bridge/feishu_bridge/pusher.py`

**类定义**:

```python
class ResultPusher:
    """结果推送器"""

    def __init__(self, lark_client):
        """
        初始化推送器
        lark_client: lark-oapi SDK 客户端
        """

    def push_success(self, chat_id: str, content: str):
        """推送成功消息"""

    def push_error(self, chat_id: str, content: str):
        """推送错误消息"""

    def push_timeout(self, chat_id: str, partial_output: str):
        """推送超时消息"""
```

**重试机制**:
- 最多 3 次重试
- 间隔 2 秒
- 失败后记录日志，不抛出异常

**消息卡片格式**:
```python
CARD_TEMPLATE = """
## Claude CLI 执行结果

**状态**: {status}

```
{output}
```

**时间**: {timestamp}
"""
```

---

## Phase 4: Execution - 精确执行

### 4.1 创建推送器模块

**文件**: `feishu-bridge/feishu_bridge/pusher.py`

**实现要点**:
- 使用 lark-oapi SDK 的消息发送 API
- 消息卡片格式化
- 重试逻辑
- 异常捕获

### 4.2 更新 main.py 集成推送器

**修改**:
- 创建 ResultPusher 实例
- CLI 执行完成后调用 pusher.push_success() 或 push_error()
- 传入 chat_id（从消息中获取）

### 4.3 日志规范

**推送日志**:
```python
logger.info(f"Pushing result to {chat_id}")
logger.debug(f"Push content: {content[:100]}...")
logger.warning(f"Push failed, retry {retry_count}/3")
logger.error(f"Push failed after retries: {error}")
```

---

## Constraints

1. **不写具体代码** - 只描述架构和接口契约
2. **异步不阻塞** - 推送失败不影响后续消息处理
3. **消息限制** - 单条消息不超过 4000 字
4. **使用 SDK** - 通过 lark-oapi SDK 推送，不自己实现 API 调用

---

## Completion Criteria

1. [ ] CLI 执行成功后飞书收到成功消息卡片
2. [ ] CLI 执行失败后飞书收到错误消息卡片
3. [ ] 推送失败时日志记录，不导致程序崩溃
4. [ ] 推送器模块可通过 `python -c "from feishu_bridge.pusher import ResultPusher"` 导入
