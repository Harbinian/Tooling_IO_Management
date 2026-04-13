# 飞书桥接服务 - CLI 执行器

---

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P0
Stage: 00103
Goal: 实现 CLI 执行器，封装 subprocess 调用 Claude CLI，支持流式输出和超时控制
Dependencies: 00102
Execution: RUNPROMPT

---

## Context

**需求背景**:
用户通过 `/claude <command>` 发送指令，服务需要调用本地 Claude CLI 并返回结果。

**本阶段目标**:
- 实现 CLIExecutor 模块
- 支持流式输出捕获
- 支持超时控制（60秒）

---

## Phase 1: PRD - 业务需求分析

**业务场景**:
用户发送 `/claude --version`，服务执行 `claude --version` 并返回输出。

**目标用户**:
- 开发者本人

**核心痛点**:
- 没有 CLI 执行器，无法调用 Claude CLI

**业务目标**:
- 执行结果准确返回
- 超时可控，不阻塞服务

---

## Phase 2: Data - 数据流转

**执行流程**:
```
/claude <command> → CLIExecutor.execute() → subprocess → stdout/stderr → 格式化 → 返回
```

**超时控制**:
- 默认 60 秒超时
- 超时后强制终止进程
- 返回已捕获的输出

---

## Phase 3: Architecture - 架构设计

**模块位置**: `feishu-bridge/feishu_bridge/executor.py`

**类定义**:

```python
class CLIExecutor:
    """Claude CLI 执行器"""

    def __init__(self, cli_path: str = "claude", timeout: int = 60):
        """
        初始化执行器
        cli_path: Claude CLI 路径
        timeout: 超时时间（秒）
        """

    def execute(self, command: str) -> ExecutionResult:
        """
        执行命令
        返回: ExecutionResult(success, stdout, stderr, timed_out)
        """
```

**接口契约**:
- `execute()` 返回的结果格式:
  ```python
  class ExecutionResult:
      success: bool           # 是否成功（exit code == 0）
      stdout: str             # 标准输出
      stderr: str             # 错误输出
      timed_out: bool        # 是否超时
      exit_code: int         # 退出码
  ```

**流式输出处理**:
- 使用 `subprocess.Popen`
- 循环读取 `stdout.readline()`
- 存入缓冲区
- 超时后 `proc.kill()`

**结果格式化**:
- 合并 stdout 和 stderr
- 限制单条消息 4000 字（飞书限制）
- 成功/失败使用不同格式

---

## Phase 4: Execution - 精确执行

### 4.1 创建执行器模块

**文件**: `feishu-bridge/feishu_bridge/executor.py`

**实现要点**:
- 使用 `subprocess.Popen` 而非 `run()`
- 流式读取 stdout/stderr
- 超时控制使用线程或信号
- 异常处理（进程崩溃、编码错误）

### 4.2 更新 main.py 集成执行器

**修改**:
- 创建 CLIExecutor 实例
- 注册 /claude 处理器
- 调用 executor.execute() 并获取结果

### 4.3 日志规范

**执行日志**:
```python
logger.info(f"Executing Claude CLI: {command}")
logger.debug(f"Command output: {stdout[:100]}...")
logger.warning(f"Command timed out after {timeout}s")
logger.error(f"Command failed: {stderr}")
```

---

## Constraints

1. **不写具体代码** - 只描述架构和接口契约
2. **超时强制终止** - 超时后必须 kill 进程
3. **编码处理** - 处理命令输出的各种编码
4. **结果限制** - 输出超过 4000 字要截断

---

## Completion Criteria

1. [ ] `/claude --version` 返回 Claude CLI 版本信息
2. [ ] `/claude echo hello` 返回 `hello`
3. [ ] 执行超时时（可用 `/claude sleep 100` 测试）60 秒后返回超时信息
4. [ ] 执行器模块可通过 `python -c "from feishu_bridge.executor import CLIExecutor"` 导入
