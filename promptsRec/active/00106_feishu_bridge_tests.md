# 飞书桥接服务 - 测试与文档

---

Primary Executor: Claude Code
Task Type: Testing
Priority: P0
Stage: 00106
Goal: 单元测试覆盖核心模块 + README 文档
Dependencies: 00105
Execution: RUNPROMPT

---

## Context

**需求背景**:
服务核心模块需要单元测试，使用文档需要完善。

**本阶段目标**:
- 实现单元测试
- 完善 README 文档

---

## Test Scope / 测试范围

**测试目标**:
- Router 模块：指令解析、去重逻辑
- Executor 模块：CLI 调用、超时处理

**测试环境**:
- pytest
- unittest.mock

**依赖项**:
- `feishu_bridge.router`
- `feishu_bridge.executor`

---

## Test Strategy / 测试策略

**测试类型**: 单元测试

**测试数据**:
- 模拟飞书消息
- 模拟 CLI 输出

**Mock/Stub 策略**:
- 使用 `unittest.mock.patch` mock CLI 调用
- 不依赖真实飞书连接

---

## Test Cases / 测试用例

### Router 测试

| ID | 场景 | 前置条件 | 操作 | 期望结果 | 优先级 |
|----|------|---------|------|---------|--------|
| T1 | 解析 /status 指令 | 无 | route(message) | instruction="status" | P0 |
| T2 | 解析 /help 指令 | 无 | route(message) | instruction="help" | P0 |
| T3 | 解析 /claude 指令 | 无 | route(message) | instruction="claude", args="echo hello" | P0 |
| T4 | 去重 - 新消息 | 无 | is_duplicate(msg_id) | False | P0 |
| T5 | 去重 - 重复消息 | 已添加 | is_duplicate(msg_id) | True | P0 |

### Executor 测试

| ID | 场景 | 前置条件 | 操作 | 期望结果 | 优先级 |
|----|------|---------|------|---------|--------|
| T6 | 执行成功 | mock subprocess | execute("echo hello") | success=True, stdout="hello" | P0 |
| T7 | 执行失败 | mock subprocess | execute("exit 1") | success=False, exit_code=1 | P0 |
| T8 | 超时处理 | mock sleep | execute("sleep 100"), timeout=1 | timed_out=True | P0 |
| T9 | 编码处理 | mock utf-8 output | execute("echo 中文") | stdout 包含中文 | P1 |

---

## Pass Criteria / 通过标准

- 所有 P0 测试用例通过
- 测试文件可独立运行: `pytest tests/`

---

## Documentation / 文档

**README.md 内容**:
1. 项目简介
2. 功能特性
3. 安装方式
4. 配置说明
5. 使用方式（所有命令）
6. 目录结构
7. 注意事项

---

## Execution / 精确执行

### 6.1 创建测试文件

**tests/test_router.py**:
```python
import pytest
from feishu_bridge.router import MessageRouter, MessageDeduplicator

class TestMessageDeduplicator:
    def test_new_message_not_duplicate(self):
        dedup = MessageDeduplicator()
        assert dedup.is_duplicate("msg1") == False

    def test_duplicate_message(self):
        dedup = MessageDeduplicator()
        dedup.add("msg1")
        assert dedup.is_duplicate("msg1") == True

class TestMessageRouter:
    def test_parse_status指令(self):
        router = MessageRouter()
        result = router.route({"content": "/status"})
        assert result.instruction == "status"

    def test_parse_claude指令_with_args(self):
        router = MessageRouter()
        result = router.route({"content": "/claude echo hello"})
        assert result.instruction == "claude"
        assert result.args == "echo hello"
```

**tests/test_executor.py**:
```python
import pytest
from unittest.mock import patch, MagicMock
from feishu_bridge.executor import CLIExecutor

class TestCLIExecutor:
    @patch('subprocess.Popen')
    def test_execute_success(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"hello\n", b"")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        executor = CLIExecutor()
        result = executor.execute("echo hello")
        assert result.success == True
        assert "hello" in result.stdout

    @patch('subprocess.Popen')
    def test_execute_timeout(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.communicate.side_effect = Exception("timeout")
        mock_proc.kill = MagicMock()
        mock_popen.return_value = mock_proc

        executor = CLIExecutor(timeout=1)
        result = executor.execute("sleep 100")
        assert result.timed_out == True
```

### 6.2 创建 README.md

**文件**: `feishu-bridge/README.md`

**内容模板**:
```markdown
# Feishu Bridge

飞书与 Claude CLI 之间的长连接双向实时通信服务。

## 功能特性

- 长连接模式（WebSocket）
- 主动推送（飞书 bot）
- CLI 执行
- 后台守护进程

## 安装

```bash
pip install -e .
```

## 配置

创建 `~/.feishu-bridge/config.yaml`:

```yaml
app_id: "your_app_id"
app_secret: "your_app_secret"
claude_cli_path: "claude"
```

或使用环境变量: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`

## 使用方式

```bash
# 前台运行（调试）
feishu-bridge run

# 后台启动
feishu-bridge start

# 查看状态
feishu-bridge status

# 停止服务
feishu-bridge stop

# 重启服务
feishu-bridge restart
```

## 目录结构

```
feishu-bridge/
├── feishu_bridge/
│   ├── client.py     # 飞书 WebSocket 客户端
│   ├── router.py    # 消息路由
│   ├── executor.py   # CLI 执行器
│   ├── pusher.py     # 结果推送
│   ├── config.py     # 配置管理
│   ├── process.py    # 进程管理
│   └── main.py       # CLI 入口
├── configs/
├── tests/
├── requirements.txt
└── setup.py
```

## 飞书配置

1. 创建飞书企业自建应用
2. 开启「使用长连接接收事件」能力
3. 配置 Bot 权限（发送消息）
4. 订阅事件: `im.message.receive_v1`
5. 获取 `app_id` 和 `app_secret`
```

---

## Constraints

1. **不写具体代码** - 测试用例和 README 是输出物，不是代码实现
2. **测试隔离** - 不依赖真实飞书连接或 CLI
3. **文档完整** - README 包含所有必要信息

---

## Completion Criteria

1. [ ] `pytest tests/test_router.py` 通过
2. [ ] `pytest tests/test_executor.py` 通过
3. [ ] README.md 包含完整安装和使用说明
4. [ ] README.md 包含目录结构说明
