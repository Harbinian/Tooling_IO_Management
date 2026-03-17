# Dev Server Launcher 编译固化规则

## 目标产物

- 可执行文件：`dist/dev_server_launcher.exe`
- 打包入口：`dev_server_launcher.spec`
- 标准构建脚本：`build-dev-launcher.ps1`（`build-dev-launcher.cmd` 仅作包装）

## 固化环境约束

- 必须使用 Python `3.13.x`
- 必须可导入 `tkinter`
- 必须安装 `pyinstaller`
- 必须安装 `requirements_launcher.txt` 中依赖（当前为 `requests>=2.31.0`）

## 固化构建命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build-dev-launcher.ps1
```

## 固化质量闸门（build-dev-launcher.ps1 内置）

1. Python 版本校验（3.13）
2. `tkinter` 运行时校验（`tkinter-ok`）
3. 依赖安装校验（`pyinstaller` + launcher requirements）
4. 执行 `PyInstaller --clean --noconfirm dev_server_launcher.spec`
5. 检查 `build/dev_server_launcher/warn-dev_server_launcher.txt`，禁止以下告警：
   - `tkinter installation is broken`
   - `missing module named tkinter`
6. 冒烟测试：启动 `dist/dev_server_launcher.exe`，4 秒内不得异常退出

## 固化 spec 规则

- 必须显式打包 Tcl/Tk：
  - `tcl8.6 -> _tcl_data`
  - `tk8.6 -> _tk_data`
- `console=False`（GUI 程序，不弹控制台）
- 保留 tkinter 和 requests 的 hidden imports

## 运行时防呆

- 启动器采用单实例锁（Windows named mutex）：
  - 重复启动直接退出，避免重复窗口/反复弹出
