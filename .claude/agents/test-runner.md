# Test Runner Agent

## Purpose

后台运行的测试执行器，不受 Claude Code auto-compact 影响。维护完整的测试状态和进度，持久化到 SQLite，支持测试中断后的续传。

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Test Runner Agent (后台进程)                                │
│                                                             │
│  - 独立运行，不受 auto-compact 影响                          │
│  - 状态持久化到 test_reports/e2e_sensing.db                │
│  - 通过消息队列或文件与主会话通信                            │
│  - 向主会话报告：进度、异常、完成状态                         │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ 消息/指令
                            │
┌─────────────────────────────────────────────────────────────┐
│  主会话 (Claude Code)                                        │
│                                                             │
│  - 发送指令："开始测试"、"继续测试"、"查看状态"、"停止"        │
│  - 接收报告：进度摘要、异常发现                                │
└─────────────────────────────────────────────────────────────┘
```

## Protocol

### 消息格式

所有消息使用 JSON 格式：

```json
{
  "type": "command" | "report" | "status" | "error",
  "run_id": "测试运行 ID",
  "timestamp": "ISO 时间戳",
  "payload": {}
}
```

### 主会话 → Agent 命令

| 命令 | payload | 说明 |
|------|---------|------|
| `start` | `{test_type: "full_workflow", users: [...]}` | 开始新测试 |
| `resume` | `{}` | 继续最近的测试 |
| `status` | `{}` | 查询当前状态 |
| `stop` | `{reason: "..."}` | 停止测试 |
| `report` | `{}` | 获取完整报告 |

### Agent → 主会话报告

| 类型 | 说明 |
|------|------|
| `started` | 测试已开始 |
| `progress` | 进度报告（每步骤后） |
| `anomaly` | 发现异常 |
| `completed` | 测试完成 |
| `failed` | 测试失败 |
| `interrupted` | 测试被中断 |
| `status_response` | status 命令的响应 |

## State Machine

```
                    ┌─────────────┐
                    │   IDLE     │ ← 没有测试运行
                    └──────┬──────┘
                           │ start
                           ▼
                    ┌─────────────┐
              ┌─────│  RUNNING   │ 正在执行测试步骤
              │     └──────┬──────┘
              │            │ step complete
              │            ▼
              │     ┌─────────────┐
              │     │  WAITING   │ 等待下一指令
              │     └──────┬──────┘
              │            │ continue
              │            ▼
              │     ┌─────────────┐
              └────►│  PAUSED    │ 断点暂停
                    └──────┬──────┘
                           │ stop / error
                           ▼
                    ┌─────────────┐
                    │ COMPLETED  │ 测试结束
                    └─────────────┘
```

## Persistence

所有状态持久化到 SQLite：

- `test_runner_state`: 当前 Agent 状态（IDLE/RUNNING/PAUSED/COMPLETED）
- `test_steps`: 步骤执行记录
- 使用 test_run_id 关联感知数据

## Execution Steps

1. **启动**: Agent 读取持久化状态，如果有 RUNNING 的测试则恢复
2. **执行**: 按测试剧本执行每一步，调用感知模块
3. **断点**: 每个检查点后写入状态，允许被中断
4. **报告**: 向主会话发送进度消息
5. **完成**: 测试结束后写入最终报告

## Trigger

This agent is triggered by:
- User command: `/test-runner start`
- User command: `/test-runner resume`
- User command: `/test-runner status`
- User command: `/test-runner stop`

## Notes

- Agent 使用 `run_in_background=true` 在后台运行
- 主会话可以随时发送 status 命令查询状态
- 发现 critical 异常时自动暂停，等待主会话指令
