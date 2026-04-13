# 飞书桥接服务 - 项目骨架

---

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P0
Stage: 00100
Goal: 建立 feishu-bridge 项目结构，可通过 feishu-bridge --help 验证
Dependencies: None
Execution: RUNPROMPT

---

## Context

**需求背景**:
飞书实时长连接桥接服务是一个独立项目，不依赖主项目。需要建立项目骨架，包括目录结构、依赖声明、CLI入口。

**本阶段目标**:
- 创建项目目录结构
- 实现配置管理模块
- 实现 CLI 入口框架
- 可通过 `feishu-bridge --help` 验证

---

## Phase 1: PRD - 业务需求分析

**业务场景**:
开发者需要通过 pip 安装 feishu-bridge，并通过命令行启动服务。

**目标用户**:
- 开发者本人

**核心痛点**:
- 没有项目骨架，无法进行后续开发

**业务目标**:
- 项目结构清晰，符合 Python 包规范
- 可通过 pip install -e . 安装
- CLI 命令行工具可用

---

## Phase 2: Data - 数据流转

**配置数据流**:
```
配置文件 (YAML) → ConfigManager → pydantic 模型 → 各模块使用
环境变量 → ConfigManager → 覆盖 YAML 配置
```

**配置字段**:
| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| app_id | string | YAML / 环境变量 | 飞书应用 ID |
| app_secret | string | YAML / 环境变量 | 飞书应用密钥 |
| claude_cli_path | string | YAML / 环境变量 | Claude CLI 路径，默认 "claude" |
| log_level | string | YAML | 日志级别，默认 "INFO" |
| log_file | string | YAML | 日志文件路径 |

---

## Phase 3: Architecture - 架构设计

**项目结构**:
```
feishu-bridge/
├── feishu_bridge/           # Python 包
│   ├── __init__.py
│   ├── config.py           # 配置管理模块
│   └── main.py             # CLI 入口
├── configs/
│   └── default.yaml        # 默认配置模板
├── tests/                  # 测试目录（后续填充）
├── requirements.txt
├── setup.py
└── README.md
```

**模块职责**:

| 模块 | 职责 | 接口契约 |
|------|------|---------|
| `config.py` | 加载配置，支持 YAML + 环境变量 | `ConfigManager.load() -> AppConfig` |
| `main.py` | CLI 入口，参数解析，命令路由 | `feishu-bridge [run\|start\|stop\|restart\|status]` |

**CLI 命令**:
| 命令 | 功能 | 状态 |
|------|------|------|
| `--help` | 显示帮助信息 | 本阶段实现 |
| `run` | 前台运行 | 本阶段框架，后续实现 |
| `start` | 后台启动 | 框架占位 |
| `stop` | 停止服务 | 框架占位 |
| `restart` | 重启服务 | 框架占位 |
| `status` | 查看状态 | 框架占位 |

---

## Phase 4: Execution - 精确执行

### 4.1 创建目录结构

```
mkdir -p feishu-bridge/feishu_bridge
mkdir -p feishu-bridge/configs
mkdir -p feishu-bridge/tests
```

### 4.2 实现配置管理 (config.py)

**功能**:
- 加载 `~/.feishu-bridge/config.yaml` 配置文件
- 支持环境变量覆盖 (`FEISHU_APP_ID`, `FEISHU_APP_SECRET`)
- 使用 pydantic 模型验证配置

**接口**:
```python
class AppConfig(BaseModel):
    app_id: str
    app_secret: str
    claude_cli_path: str = "claude"
    log_level: str = "INFO"
    log_file: Optional[str] = None

def load_config() -> AppConfig:
    """加载配置，YAML 优先，环境变量覆盖"""
```

**验证规则**:
- `app_id`: 非空字符串
- `app_secret`: 非空字符串
- `claude_cli_path`: 非空字符串，指向可执行文件

### 4.3 实现 CLI 入口 (main.py)

**功能**:
- 使用 click 或 argparse 解析命令行参数
- `--help` 显示帮助
- `run` 命令启动前台模式
- 其他命令输出 "Not implemented yet"

**入口点**:
```python
# setup.py
entry_points={
    'console_scripts': [
        'feishu-bridge=feishu_bridge.main:cli',
    ],
}
```

### 4.4 创建配置文件

**configs/default.yaml**:
```yaml
# 飞书应用配置
app_id: ""  # 环境变量: FEISHU_APP_ID
app_secret: ""  # 环境变量: FEISHU_APP_SECRET

# Claude CLI 配置
claude_cli_path: "claude"  # 环境变量: CLAUDE_CLI_PATH

# 日志配置
log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
log_file: null  # null 表示输出到 stdout
```

### 4.5 创建依赖文件

**requirements.txt**:
```
lark-oapi>=1.0.0
loguru>=0.7.0
pydantic>=2.0.0
pyyaml>=6.0
click>=8.0.0
```

**setup.py**:
```python
from setuptools import setup, find_packages

setup(
    name="feishu-bridge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "lark-oapi>=1.0.0",
        "loguru>=0.7.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'feishu-bridge=feishu_bridge.main:cli',
        ],
    },
)
```

---

## Constraints

1. **不写具体代码** - 只描述模块职责和接口契约
2. **配置与代码分离** - 配置在 YAML，不写死
3. **环境变量优先** - 密钥不写在代码或 YAML 中
4. **无占位符** - 所有代码必须完整可执行

---

## Completion Criteria

1. [ ] `feishu-bridge --help` 输出帮助信息
2. [ ] `feishu-bridge run` 输出 "Config not loaded" 或类似提示（框架占位）
3. [ ] `pip install -e .` 成功安装
4. [ ] 配置文件模板 `configs/default.yaml` 存在
5. [ ] 配置管理模块可通过 `python -c "from feishu_bridge.config import load_config"` 导入
