# 飞书桥接服务 - 进程管理

---

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P0
Stage: 00105
Goal: 实现进程管理，支持 start/stop/restart/status 后台运行
Dependencies: None
Execution: RUNPROMPT

---

## Context

**需求背景**:
服务需要以后台守护进程方式运行，支持 start/stop/restart/status 管理命令。

**本阶段目标**:
- 实现 ProcessManager 模块
- 支持后台守护进程运行
- CLI 命令完整实现

---

## Phase 1: PRD - 业务需求分析

**业务场景**:
用户通过 `feishu-bridge start` 启动后台服务，通过 `feishu-bridge stop` 停止。

**目标用户**:
- 开发者本人

**核心痛点**:
- 没有进程管理，只能前台运行

**业务目标**:
- 后台稳定运行
- 进程管理可靠

---

## Phase 2: Data - 数据流转

**后台运行流程**:
```
start → fork 进程 → 写入 PID 文件 → 主进程退出 → 子进程运行
stop → 读取 PID → 发送 SIGTERM → 等待退出 → 删除 PID 文件
```

**PID 文件**: `~/.feishu-bridge/feishu-bridge.pid`

---

## Phase 3: Architecture - 架构设计

**模块位置**: `feishu-bridge/feishu_bridge/process.py`

**类定义**:

```python
class ProcessManager:
    """进程管理器"""

    def __init__(self, pid_file: str = None):
        """
        初始化进程管理器
        pid_file: PID 文件路径，默认 ~/.feishu-bridge/feishu-bridge.pid
        """

    def start(self, daemonize: bool = True):
        """启动服务"""

    def stop(self):
        """停止服务"""

    def restart(self):
        """重启服务"""

    def status(self) -> bool:
        """检查服务运行状态，返回 True/False"""

    def is_running(self) -> bool:
        """检查进程是否运行"""
```

**CLI 命令映射**:
| 命令 | ProcessManager 方法 |
|------|---------------------|
| `feishu-bridge start` | `start()` |
| `feishu-bridge stop` | `stop()` |
| `feishu-bridge restart` | `restart()` |
| `feishu-bridge status` | `status()` |

**守护进程实现**:
- Unix: `os.fork()` + `setsid()`
- Windows: 使用 `nssm` 或 `pywin32`（可选，本阶段优先实现 Unix）

---

## Phase 4: Execution - 精确执行

### 4.1 创建进程管理模块

**文件**: `feishu-bridge/feishu_bridge/process.py`

**实现要点**:
- PID 文件读写
- fork/demonize（Unix）
- SIGTERM 信号处理
- 优雅退出

### 4.2 更新 main.py CLI 命令

**修改**:
```python
# main.py
@cli.command()
def start():
    """Start service in background"""
    manager.start()

@cli.command()
def stop():
    """Stop service"""
    manager.stop()

@cli.command()
def restart():
    """Restart service"""
    manager.restart()

@cli.command()
def status():
    """Show service status"""
    if manager.status():
        click.echo("Service is running")
    else:
        click.echo("Service is not running")
```

### 4.3 日志规范

**进程管理日志**:
```python
logger.info("Starting service in background...")
logger.info(f"Service started with PID {pid}")
logger.info("Stopping service...")
logger.info("Service stopped")
logger.warning("Service is not running")
logger.error(f"Failed to start service: {error}")
```

---

## Constraints

1. **不写具体代码** - 只描述架构和接口契约
2. **PID 文件原子操作** - 写入和读取要安全
3. **信号处理优雅退出** - 捕获 SIGTERM，清理资源
4. **跨平台优先 Unix** - Windows 支持可后续补充

---

## Completion Criteria

1. [ ] `feishu-bridge start` 后台启动服务
2. [ ] `feishu-bridge status` 显示运行状态
3. [ ] `feishu-bridge stop` 停止服务
4. [ ] `feishu-bridge restart` 重启服务
5. [ ] 进程管理模块可通过 `python -c "from feishu_bridge.process import ProcessManager"` 导入
