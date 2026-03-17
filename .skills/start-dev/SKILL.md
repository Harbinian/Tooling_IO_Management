# 启动开发环境技能 / Start Dev Environment Skill

## 目的 / Purpose

通过统一启动器 `dist/dev_server_launcher.exe` 启动项目开发环境。  
Start the project dev environment through the unified launcher `dist/dev_server_launcher.exe`.

## 使用方法 / Usage

```text
/start-dev
```

## 端口 / Ports

| 服务 / Service | 端口 / Port |
|---|---|
| 前端 / Frontend | 8150 |
| 后端 / Backend | 8151 |

## 标准启动命令 / Standard Start Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start-dev.ps1
```

`start-dev.ps1` 会调用：

```powershell
.\dist\dev_server_launcher.exe
```

## 行为 / Behavior

1. 检查 `dist/dev_server_launcher.exe` 是否存在。  
2. 启动 launcher 进程。  
3. 验证端口 `8150/8151` 是否监听。  
4. 输出访问地址与日志目录 `logs/dev_server_launcher/`。  

## 验证 / Verification

```powershell
curl http://localhost:8151/api/health
```

前端访问：`http://localhost:8150`。  
