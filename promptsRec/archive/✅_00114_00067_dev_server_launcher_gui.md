# Prompt: 010_dev_server_launcher_gui_improvement

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 067
Goal: Optimize dev_server_launcher.py GUI layout and declare service addresses
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

dev_server_launcher.py 是工装出入库管理系统的开发服务器启动工具（Python tkinter GUI）。当前存在以下问题：

1. **端口配置不一致**：GUI 中后端端口硬编码为 8151，但实际使用 `BACKEND_PORT = 8151`；前端端口硬编码为 8150，但 Vite 实际可能运行在不同端口
2. **缺少服务地址声明**：用户无法直接在 GUI 上看到前端 http://localhost:8150 和后端 http://localhost:8151 的明确地址
3. **UI 可优化**：当前布局较为简单，可以增加服务状态可视化、地址点击复制等功能

**当前状态**：
- 后端：Flask 运行在 port 8151
- 前端：Vite 运行在 port 8150
- 用户反馈：GUI 显示健康，但访问 http://localhost:8150 时白屏

---

## Required References / 必需参考

- `dev_server_launcher.py` - 当前实现
- `vite.config.js` - 前端端口配置
- `web_server.py` - 后端端口配置
- `config/settings.py` - 集中配置

---

## Core Task / 核心任务

优化 dev_server_launcher.py 的 GUI 界面，明确显示服务地址，并检查潜在 bug。

---

## Required Work / 必需工作

### 1. 优化 GUI 布局和视觉效果
- 增加服务状态可视化面板
- 添加服务地址显示区域（带复制按钮）
- 优化按钮布局和间距
- 添加状态指示器（绿色=健康，红色=异常，橙色=警告）

### 2. 明确声明服务地址
在 GUI 上清晰显示：
- **前端地址**: http://localhost:8150
- **后端地址**: http://localhost:8151
- **健康检查接口**: http://localhost:8151/api/health

### 3. 检查并修复潜在 Bug
- 检查端口配置是否与实际服务端口一致
- 检查进程启动/停止逻辑是否有竞态条件
- 检查日志文件写入是否有线程安全问题
- 检查后端健康检查的 timeout 设置是否合理

### 4. 增强用户体验
- 添加"打开浏览器"按钮直接访问前端
- 添加服务响应时间显示
- 添加最后更新时间戳

---

## Constraints / 约束条件

1. **不要破坏现有功能**：启动/停止/重启按钮必须正常工作
2. **保持中文界面**：所有标签和消息使用中文
3. **线程安全**：确保多线程操作不会导致 UI 卡死或数据竞争
4. **错误处理**：所有网络请求必须设置合理的 timeout
5. **编码**：必须使用 UTF-8 编码

---

## Completion Criteria / 完成标准

1. **GUI 启动后清晰显示**：
   - 前端地址: http://localhost:8150 （带"打开"按钮）
   - 后端地址: http://localhost:8151/api/health （带"打开"按钮）

2. **状态指示器正常工作**：
   - 绿色圆点 = 服务健康
   - 红色圆点 = 服务停止
   - 橙色圆点 = 服务运行中但健康检查失败

3. **服务控制按钮功能正常**：
   - 启动全部 / 停止全部 / 重启全部
   - 单个服务启动/停止/重启

4. **无线程安全问题**：
   - 使用 `root.after()` 更新 UI 而非直接修改
   - 日志写入使用合适的锁或队列

5. **错误处理完善**：
   - 健康检查 timeout = 2 秒
   - 网络异常不会导致 GUI 崩溃

6. **语法检查通过**：
   ```bash
   python -m py_compile dev_server_launcher.py
   ```
