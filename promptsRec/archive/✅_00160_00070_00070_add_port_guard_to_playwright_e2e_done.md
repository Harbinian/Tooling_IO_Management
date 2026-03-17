# Human E2E Tester P3 问题修复：playwright_e2e.py 端口守卫

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P3
Stage: 00070
Goal: 在 playwright_e2e.py 中实现 8150/8151 端口强检查，缺失则立即退出
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

根据 `test_reports/HUMAN_E2E_SKILL_FINAL_RETEST_REPORT_20260327.md`：

### P3-1: 端口前置检查仅文档化，执行层落实不完整

**现象**：
- `skill.md` 明确要求 8150/8151 强检查与失败即退出
- `api_e2e.py` 增加了后端健康检查（有改进）
- `playwright_e2e.py` 仍未实现同等级端口守卫

**影响**：执行稳定性依赖人工环境准备

---

## Required References / 必需参考

1. `test_runner/playwright_e2e.py` - 需要修改的执行器
2. `.skills/human-e2e-tester/skill.md` - 技能定义（端口检查要求）
3. `test_runner/api_e2e.py` - 参考已有的端口检查实现

---

## Core Task / 核心任务

### 端口检查要求

根据 `skill.md`：

| Service | Port | URL |
|---------|------|-----|
| Frontend | 8150 | http://localhost:8150 |
| Backend | 8151 | http://localhost:8151 |

### 实现检查逻辑

```python
# 端口检查函数
def check_services():
    """检查前端和后端服务是否在所需端口运行"""
    frontend = Test-NetConnection -ComputerName localhost -Port 8150
    backend = Test-NetConnection -ComputerName localhost -Port 8151

    if (-not frontend.TcpTestSucceeded -or -not backend.TcpTestSucceeded):
        Write-Host "[ABORT] Services not ready" -ForegroundColor Red
        return False
    return True
```

### 在 playwright_e2e.py 中实现

1. 在 `main()` 函数开头调用端口检查
2. 如果检查失败，打印错误消息并以 exit code 1 退出
3. 错误消息应明确指出哪些端口未响应

---

## Required Work / 必需工作

- [ ] Step 1: 在 `playwright_e2e.py` 开头添加端口检查函数
- [ ] Step 2: 在 `main()` 函数开头调用检查
- [ ] Step 3: 失败时打印清晰错误消息并退出
- [ ] Step 4: 测试：停止服务后运行，应显示错误并退出

---

## Constraints / 约束条件

- **Windows 兼容**：使用 PowerShell 或 Python 标准库进行端口检查
- **快速失败**：检查失败应立即退出，不执行后续代码
- **清晰消息**：错误消息应告知用户哪些服务未运行

---

## Completion Criteria / 完成标准

1. `playwright_e2e.py` 在服务未运行时以 exit code 1 退出
2. 错误消息明确指出 Frontend (8150) 和/或 Backend (8151) 未响应
3. 服务运行时正常执行测试
4. 与 `api_e2e.py` 的端口检查行为一致
