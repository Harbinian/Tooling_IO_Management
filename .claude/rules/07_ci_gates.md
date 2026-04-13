# CI 自动化门禁规范 / CI Gates Protocol

---

## 目的 / Purpose

将所有可客观验证的规则转化为自动化门禁，最小化人工介入节点。
人工审核仅保留 AI 无法判断的业务语义场景。

---

## 人工介入边界声明 / Human-in-the-Loop Boundary

以下场景**必须**人工介入，其余全部由 CI 自动判断：

| # | 场景 | 介入形式 | 预计耗时 |
|---|------|---------|---------|
| H1 | 业务逻辑正确性验收 | 阅读 PRD + 确认功能符合工厂流程 | ≤ 15 min |
| H2 | 前端页面功能验收 | 操作页面确认交互符合使用习惯 | ≤ 10 min |
| H3 | RBAC 权限矩阵变更 | 确认"谁能看什么"符合组织规则 | ≤ 10 min |
| H4 | HOTFIX 触发决策 | 判断问题是否紧急到需要绕过完整流程 | ≤ 5 min |

> ⚠️ 除以上 4 个节点外，任何"我觉得应该人工看一下"的冲动都应转化为新的自动化门禁。

---

## 门禁层级 / Gate Layers

```
Commit Push
    │
    ├── Layer 1: pre-commit hooks        （本地，秒级）
    ├── Layer 2: CI Static Analysis      （远程，< 2 min）
    ├── Layer 3: CI Test Gates           （远程，< 10 min）
    ├── Layer 4: CI Structure Checks     （远程，< 1 min）
    └── Layer 5: CI Archive Guards       （远程，< 1 min）
```

全部通过后，仅触发 H1/H2（新功能）或直接归档（纯修复/测试任务）。

---

## Layer 1 — Pre-commit Hooks

**工具**: `pre-commit` framework
**触发时机**: `git commit` 前本地执行
**不通过**: 拒绝 commit，无需人工介入

### G1-1｜UTF-8 编码检测

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  hooks:
    - id: check-byte-order-marker   # 检测 BOM
    - id: mixed-line-ending         # 检测混合换行符
```

**对应规则**: `00_core.md` — 编码章节

---

### G1-2｜中文字段名字面量检测

```yaml
- repo: local
  hooks:
    - id: no-chinese-sql-literal
      name: Detect Chinese SQL literals
      language: pygrep
      entry: '(SELECT|INSERT|UPDATE|DELETE|WHERE|FROM).*[\u4e00-\u9fff]'
      files: \.py$
      args: [--multiline]
```

**对应规则**: `00_core.md` — 字段名常量使用规范
**说明**: 检测 Python 文件中 SQL 语句内出现的中文字符，`column_names.py` 本身豁免

---

### G1-3｜占位符代码检测

```yaml
- repo: local
  hooks:
    - id: no-placeholder-code
      name: Detect placeholder code
      language: pygrep
      entry: '(^\s*\.\.\.\s*$|^\s*pass\s*#\s*TODO|raise\s+NotImplementedError)'
      files: \.(py|ts|vue)$
```

**对应规则**: `00_core.md` — Zero-Assumption Policy
**豁免**: 抽象基类中的 `raise NotImplementedError` 允许，需在行尾添加 `# abstract` 注释

---

### G1-4｜敏感信息检测

```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```

**对应规则**: `00_core.md` — 敏感信息处理
**说明**: 首次运行 `detect-secrets scan > .secrets.baseline` 生成基线，误报在基线中标记豁免

---

### G1-5｜依赖版本锁定检测

```yaml
- repo: local
  hooks:
    - id: check-dependency-pinning
      name: Check dependency pinning
      language: python
      entry: python scripts/check_pinning.py
      files: requirements.*\.txt$
```

```python
# scripts/check_pinning.py
import sys, re, pathlib

def check(path):
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    violations = [
        l for l in lines
        if l.strip() and not l.startswith("#")
        and not re.search(r'==[\d]', l)
    ]
    if violations:
        print(f"[FAIL] Unpinned dependencies in {path}:")
        for v in violations: print(f"  {v}")
        sys.exit(1)

for f in sys.argv[1:]:
    check(f)
```

**对应规则**: `00_core.md` — 依赖管理

---

## Layer 2 — CI Static Analysis

**工具**: GitHub Actions / GitLab CI
**触发时机**: Push / PR
**不通过**: 自动阻断 merge，无需人工介入

### G2-1｜Python 静态分析

```yaml
# .github/workflows/static.yml
- name: Ruff lint
  run: ruff check backend/ --select E,W,F,I --exit-non-zero-on-fix

- name: Ruff format check
  run: ruff format backend/ --check
```

---

### G2-2｜前端静态分析

```yaml
- name: ESLint
  run: npx eslint frontend/src --ext .ts,.vue --max-warnings 0
```

#### ESLint 自定义规则 A：禁止硬编码颜色

```javascript
// eslint-rules/no-hardcoded-color.js
module.exports = {
  meta: { type: "problem" },
  create(context) {
    return {
      Literal(node) {
        if (typeof node.value === "string" &&
            /(#[0-9a-fA-F]{3,6}|rgb\(|rgba\(|hsl\()/.test(node.value)) {
          context.report({
            node,
            message: "禁止硬编码颜色，必须使用 CSS 变量 var(--*)"
          });
        }
      }
    };
  }
};
```

**对应规则**: `04_frontend.md` — CSS 变量规范

---

#### ESLint 自定义规则 B：v-debug-id 必须存在

```javascript
// eslint-rules/require-v-debug-id.js
const REQUIRED_TAGS = ["Card", "header", "section", "Button"];
const ID_PATTERN = /^[A-Z]+-[A-Z]+-\d{3}$/;

module.exports = {
  meta: { type: "problem" },
  create(context) {
    return {
      VElement(node) {
        if (!REQUIRED_TAGS.includes(node.rawName)) return;
        const attr = node.startTag.attributes.find(
          a => a.key?.name === "v-debug-id" || a.key?.argument?.name === "debug-id"
        );
        if (!attr) {
          context.report({ node, message: `<${node.rawName}> 缺少 v-debug-id 属性` });
          return;
        }
        const val = attr.value?.value;
        if (val && !ID_PATTERN.test(val)) {
          context.report({ node, message: `v-debug-id "${val}" 格式错误，应为 PAGE-TYPE-000` });
        }
      }
    };
  }
};
```

**对应规则**: `04_frontend.md` — DEBUG_ID 规范

---

### G2-3｜外部表 DDL 操作检测

```yaml
- name: Check external table DDL
  run: python scripts/check_external_ddl.py
```

```python
# scripts/check_external_ddl.py
import ast, sys, pathlib, re

EXTERNAL_TABLES = ["Tooling_ID_Main"]
DDL_KEYWORDS = ["CREATE", "ALTER", "DROP", "TRUNCATE"]
violations = []

for f in pathlib.Path("backend").rglob("*.py"):
    src = f.read_text(encoding="utf-8")
    for kw in DDL_KEYWORDS:
        for tbl in EXTERNAL_TABLES:
            if re.search(rf'{kw}.*{tbl}', src, re.IGNORECASE):
                violations.append(f"{f}: {kw} on {tbl}")

if violations:
    print("[FAIL] DDL on external tables detected:")
    for v in violations: print(f"  {v}")
    sys.exit(1)
```

**对应规则**: `00_core.md` — 外部系统表访问规范

---

## Layer 3 — CI Test Gates

**工具**: pytest / Vitest / Playwright
**触发时机**: Push / PR
**不通过**: 自动阻断，无需人工介入

### G3-1｜Python 单元测试覆盖率门禁

```yaml
- name: Unit test coverage
  run: |
    pytest tests/unit \
      --cov=backend \
      --cov-fail-under=80 \
      --cov-report=xml:coverage.xml \
      --cov-report=term-missing
```

**对应规则**: `06_testing.md` — 单元测试覆盖率 ≥ 80%

---

### G3-2｜集成测试覆盖率门禁

```yaml
- name: Integration test coverage
  run: |
    pytest tests/integration \
      --cov=backend \
      --cov-fail-under=60 \
      --cov-report=xml:coverage_integration.xml
```

**对应规则**: `06_testing.md` — 集成测试覆盖率 ≥ 60%

---

### G3-3｜前端单元测试

```yaml
- name: Frontend unit tests
  run: npx vitest run --coverage --coverage.thresholds.lines=80
```

---

### G3-4｜E2E P0 路径覆盖检测

```yaml
- name: E2E P0 paths
  run: npx playwright test --grep @P0
```

```typescript
// P0 路径必须在测试中标记 @P0 tag
// playwright.config.ts 中定义 P0 清单路径
// scripts/check_p0_coverage.ts 比对清单与实际执行报告
```

**对应规则**: `06_testing.md` — E2E 覆盖全部 P0 路径
**说明**: P0 清单维护在 `docs/p0_paths.yaml`，由人工在 H1 节点更新

---

## Layer 4 — CI Structure Checks

**说明**: `02_debug.md` D3/D5/D6 挂起节点的自动化预检，替代人工对文档结构的初步检查。**不替代 reviewer 评分**，两者独立。
**触发**: Push / PR（8D 任务）
**不通过**: 自动阻断，无需人工介入

### G4-1｜8D 文档结构检测

```yaml
- name: 8D document structure check
  run: python scripts/check_8d_structure.py
  if: contains(github.event.pull_request.labels.*.name, '8D')
```

```python
# scripts/check_8d_structure.py
# CI 自动执行的 8D 文档结构预检
# 检测 8D 文档是否包含所有必要章节

import sys, pathlib, re

REQUIRED_SECTIONS = {
    "D2": ["What", "Where", "When", "Why"],   # 5W2H 结构
    "D3": ["临时措施", "爆炸半径"],
    "D4": ["根因", "Why"],                     # 5 Whys 至少出现
    "D5": ["永久对策", "修改文件"],
    "D6": ["测试", "验证"],
}

def check_doc(path):
    content = pathlib.Path(path).read_text(encoding="utf-8")
    failures = []
    for section, keywords in REQUIRED_SECTIONS.items():
        if not any(kw in content for kw in keywords):
            failures.append(f"{section}: 缺少关键词 {keywords}")
    return failures

# 扫描 promptsRec/active/ 目录中 bug 编号范围的文档
for f in pathlib.Path("promptsRec/active").glob("1*.md"):
    failures = check_doc(f)
    if failures:
        print(f"[FAIL] {f.name} 8D 结构不完整:")
        for fail in failures: print(f"  {fail}")
        sys.exit(1)

print("[PASS] 8D document structure OK")
```

**对应规则**: `02_debug.md` — D3/D5/D6 挂起节点（与 reviewer 评分互为独立环节）

---

### G4-2｜HOTFIX RFC 文档结构检测

```yaml
- name: HOTFIX RFC structure check
  run: python scripts/check_hotfix_rfc.py
  if: contains(github.event.pull_request.labels.*.name, 'hotfix')
```

```python
# scripts/check_hotfix_rfc.py
REQUIRED_RFC_SECTIONS = ["爆炸半径", "回滚预案", "影响模块"]

for f in pathlib.Path("promptsRec/active").glob("hotfix_*.md"):
    content = f.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_RFC_SECTIONS if s not in content]
    if missing:
        print(f"[FAIL] {f.name} RFC 缺少章节: {missing}")
        sys.exit(1)
```

**对应规则**: `03_hotfix.md` — Step 2 RFC 文档要求

---

## Layer 5 — CI Archive Guards

**说明**: 替代 `05_task_convention.md` 中的人工归档前置检查
**触发时机**: 归档 PR（将文件从 `active/` 移入 `archive/`）

### G5-1｜归档文件命名格式校验

```yaml
- name: Archive naming format check
  run: python scripts/check_archive_naming.py
```

```python
# scripts/check_archive_naming.py
import sys, re, pathlib

ARCHIVE_PATTERN = re.compile(
    r'^✅_\d{5}_\d{5}_[a-z][a-z0-9_]+_done\.md$'
)
ACTIVE_PATTERN = re.compile(
    r'^\d{5}_[a-z][a-z0-9_]+\.md$'
)

failures = []

for f in pathlib.Path("promptsRec/archive").iterdir():
    if not ARCHIVE_PATTERN.match(f.name):
        failures.append(f"archive/ 命名不合规: {f.name}")

for f in pathlib.Path("promptsRec/active").iterdir():
    if f.name == ".gitkeep": continue
    if not ACTIVE_PATTERN.match(f.name):
        failures.append(f"active/ 命名不合规: {f.name}")

if failures:
    for fail in failures: print(f"[FAIL] {fail}")
    sys.exit(1)
```

**对应规则**: `05_task_convention.md` — 命名格式

---

### G5-2｜执行顺序号唯一性校验

```python
# scripts/check_archive_naming.py（追加到上方脚本）

seq_nums = []
for f in pathlib.Path("promptsRec/archive").iterdir():
    m = re.match(r'^✅_(\d{5})_', f.name)
    if m: seq_nums.append((m.group(1), f.name))

seen, dupes = set(), []
for num, name in seq_nums:
    if num in seen: dupes.append(f"重复执行顺序号 {num}: {name}")
    seen.add(num)

if dupes:
    for d in dupes: print(f"[FAIL] {d}")
    sys.exit(1)
```

**对应规则**: `05_task_convention.md` — 执行顺序号唯一性

---

### G5-3｜归档前测试报告存在性校验

```yaml
- name: Archive pre-condition check
  run: python scripts/check_archive_precondition.py
```

```python
# scripts/check_archive_precondition.py
# 确认归档文件对应的测试报告存在且全绿

import sys, json, pathlib, re

REPORT_DIR = pathlib.Path("logs/prompt_task_runs")

def find_report_for_task(task_id):
    for report in REPORT_DIR.glob("*.md"):
        name = report.name
        content = report.read_text(encoding="utf-8", errors="ignore")
        if task_id in name or f"提示词编号: {task_id}" in content or f"**ID**: {task_id}" in content:
            return report
    return None

for f in pathlib.Path("promptsRec/archive").iterdir():
    m = re.match(r'^✅_\d{5}_(\d{5})_', f.name)
    if not m: continue
    task_id = m.group(1)
    report = find_report_for_task(task_id)

    if report is None:
        print(f"[FAIL] {f.name}: 缺少测试报告 {report}")
        sys.exit(1)

print("[PASS] Archive preconditions OK")
```

**对应规则**: `05_task_convention.md` — 归档前置条件

---

## 门禁 × 规则映射总表 / Gate-to-Rule Matrix

| 门禁 ID | 替代的人工节点 | 对应规则文件 | 工具 |
|--------|-------------|------------|------|
| G1-1 | UTF-8 人工检查 | `00_core.md` | pre-commit |
| G1-2 | SQL 字段名 Code Review | `00_core.md` | pygrep |
| G1-3 | 占位符 Code Review | `00_core.md` | pygrep |
| G1-4 | 敏感信息 Code Review | `00_core.md` | detect-secrets |
| G1-5 | 依赖版本 Code Review | `00_core.md` | 自定义脚本 |
| G2-1 | Python Code Review | `00_core.md` | Ruff |
| G2-2 | 前端 Code Review | `04_frontend.md` | ESLint |
| G2-3 | 外部表 DDL Code Review | `00_core.md` | 自定义脚本 |
| G3-1 | tester 单元测试确认 | `06_testing.md` | pytest-cov |
| G3-2 | tester 集成测试确认 | `06_testing.md` | pytest-cov |
| G3-3 | tester 前端测试确认 | `06_testing.md` | Vitest |
| G3-4 | tester E2E 冒烟测试 | `06_testing.md` | Playwright |
| G4-1 | reviewer D3/D5/D6 评分前的结构预检 | `02_debug.md` | 自定义脚本 |
| G4-2 | tester HOTFIX 冒烟确认 | `03_hotfix.md` | 自定义脚本 |
| G5-1 | 归档命名人工检查 | `05_task_convention.md` | 自定义脚本 |
| G5-2 | 归档序号人工检查 | `05_task_convention.md` | 自定义脚本 |
| G5-3 | 归档前置条件人工确认 | `05_task_convention.md` | 自定义脚本 |

---

## 残余人工节点说明 / Residual Human Nodes

以下节点**有意保留人工**，不应被自动化替代：

| 节点 | 保留原因 | 触发条件 |
|------|---------|---------|
| H1 业务逻辑验收 | AI 不具备工厂现场知识 | 每个功能任务 PR |
| H2 前端页面验收 | 交互体验无法量化 | 每个含 UI 变更的 PR |
| H3 RBAC 矩阵变更 | 权限是业务决策非技术决策 | `docs/RBAC_PERMISSION_MATRIX.md` 变更时 |
| H4 HOTFIX 触发 | 生产风险判断需要业务上下文 | 生产告警时 |
| H5 P0 清单维护 | P0 定义是业务优先级判断 | PRD 变更时 |

---

## Layer 6 — 技能文件门禁 / Skill File Gates

**触发条件**: `C:\Users\charl\.claude\skills\` 目录下有文件变更时执行
**执行者**: CI 自动执行，无需人工介入

---

### G6-1｜体积检查

**检查范围**: 所有变更的技能文件

| 状态 | 阈值 | 处理方式 |
|------|------|---------|
| 正常 | ≤ 20KB | 无需处理 |
| 警告 | 15KB ~ 20KB | 须在 PR 说明中解释原因，不阻断 |
| 阻断 | > 20KB | CI 拦截，必须外部化数据后方可合并 |

**错误信息**:
```
[G6-1] {filename} 体积 {size}KB 超过 20KB 限制，
请将以下内容外部化后重新提交：路径列表 / 测试数据 / 重复流程片段
```

---

### G6-2｜Frontmatter 完整性检查

**检查范围**: 所有变更的技能文件

必填字段: `name / executor / auto_invoke / depends_on / triggers / rules_ref / version`

| 检查项 | 规则 | 不通过时 |
|--------|------|---------|
| 必填字段缺失 | 任意必填字段缺失 → 阻断合并 | 阻断 |
| executor 合法性 | 值不在合法列表（Claude Code / Codex / Human）→ 阻断 | 阻断 |
| name 与技能目录名匹配 | `SKILL.md` / `skill.md` 的 frontmatter `name` 与父目录名不一致 → 阻断 | 阻断 |

**错误信息**:
```
[G6-2] {filename} Frontmatter 不合规：缺少字段 {fields} / executor 值非法 / name 与技能目录名不匹配
```

---

### G6-3｜触发命令全局唯一性检查

**检查范围**: `C:\Users\charl\.claude\skills\` 目录所有技能文件（全量扫描，非仅变更文件）

| 检查项 | 规则 | 不通过时 |
|--------|------|---------|
| 命令重复 | 任意两个技能文件的 triggers 存在重复命令 → 阻断合并 | 阻断 |

**错误信息**:
```
[G6-3] 触发命令冲突：/{command} 同时出现在 {file_a} 和 {file_b}，
请修改其中一个技能的触发命令
```

---

### G6-4｜depends_on 引用存在性检查

**检查范围**: 所有变更的技能文件

| 检查项 | 规则 | 不通过时 |
|--------|------|---------|
| 依赖引用 | `depends_on` 中声明的技能名称在 `C:\Users\charl\.claude\skills\` 目录中不存在对应文件 → 阻断合并 | 阻断 |

**错误信息**:
```
[G6-4] {filename} 声明依赖 {skill_name}，
但 C:\Users\charl\.claude\skills\{skill_name}/ 不存在，请先创建依赖技能或修正 depends_on
```

---

### G6-5｜元技能保护检查

**检查范围**: 所有变更的技能文件

| 检查项 | 规则 | 不通过时 |
|--------|------|---------|
| 元技能 auto_invoke | 文件名前缀为 `skill-` 且 `auto_invoke: true` → 阻断合并 | 阻断 |

**错误信息**:
```
[G6-5] {filename} 是元技能，auto_invoke 必须为 false
```

---

### Layer 6 门禁汇总

| 门禁 | 检查内容 | 不通过时 |
|------|---------|---------|
| G6-1 | 文件体积 ≤ 20KB | 阻断（>20KB）/ 警告（15-20KB） |
| G6-2 | Frontmatter 完整且合法 | 阻断 |
| G6-3 | 触发命令全局唯一 | 阻断 |
| G6-4 | depends_on 引用存在 | 阻断 |
| G6-5 | 元技能 auto_invoke 为 false | 阻断 |

**Layer 6 全部通过** → 技能文件变更允许合并
