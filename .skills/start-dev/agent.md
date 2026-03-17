# 启动开发环境代理 / Start Dev Environment Agent

## 角色 / Role

使用 `dist/dev_server_launcher.exe` 启动开发环境。  
Starts the dev environment via `dist/dev_server_launcher.exe`.

## 单一入口 / Single Entry

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start-dev.ps1
```

## 固定端口 / Fixed Ports

- 前端 / Frontend: `http://localhost:8150`
- 后端 / Backend: `http://localhost:8151`

## 行为约束 / Behavior Rules

1. 必须使用 launcher，不再直接拉起 `python web_server.py` 或 `npm run dev`。  
2. 若 `dist/dev_server_launcher.exe` 不存在，直接报错并停止。  
3. 启动后验证 `8150/8151` 监听状态。  
4. 日志目录统一为 `logs/dev_server_launcher/`。  

## 验证 / Verification

```powershell
curl http://localhost:8151/api/health
```
