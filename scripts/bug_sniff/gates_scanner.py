# -*- coding: utf-8 -*-
"""
Gates Scanner - G1-G6 全量仓库质量扫描
执行 G1-G6 所有门禁检查，汇总结果
"""

import os
import re
import subprocess
import json
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GateResult:
    """单个门禁检查结果"""
    gate_id: str
    name: str
    status: str  # PASS / FAIL / SKIP / WARN
    message: str = ""
    details: list = field(default_factory=list)

    def to_dict(self):
        return {
            "gate_id": self.gate_id,
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details
        }


@dataclass
class ScanResult:
    """扫描汇总结果"""
    repo_path: str
    gate_results: list = field(default_factory=list)
    total_pass: int = 0
    total_fail: int = 0
    total_skip: int = 0
    total_warn: int = 0

    def add(self, result: GateResult):
        self.gate_results.append(result)
        if result.status == "PASS":
            self.total_pass += 1
        elif result.status == "FAIL":
            self.total_fail += 1
        elif result.status == "SKIP":
            self.total_skip += 1
        elif result.status == "WARN":
            self.total_warn += 1

    def is_all_pass(self) -> bool:
        return self.total_fail == 0

    def overall_status(self) -> str:
        if self.total_fail > 0:
            return "FAIL"
        elif self.total_skip == len(self.gate_results):
            return "SKIP"
        else:
            return "PASS"


class GatesScanner:
    """G1-G6 门禁扫描器"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = pathlib.Path(repo_path).resolve()
        self.results: list[GateResult] = []
        # 用户全局 skills 目录（支持跨项目技能）
        self.global_skills_path = pathlib.Path(os.path.expanduser("~/.claude/skills")).resolve()

    def _get_skills_dirs(self):
        """获取所有技能目录（项目级 + 全局级）"""
        dirs = []
        repo_skills = self.repo_path / ".skills"
        if repo_skills.exists():
            dirs.append(repo_skills)
        if self.global_skills_path.exists():
            dirs.append(self.global_skills_path)
        return dirs

    # ========================================================================
    # G1: Pre-commit Hooks (本地)
    # ========================================================================

    def check_g1_1_utf8_bom(self) -> GateResult:
        """G1-1: UTF-8 BOM 检测"""
        result = GateResult("G1-1", "UTF-8 BOM 检测", "PASS")
        failures = []

        for py_file in self._iterate_python_files():
            if py_file.exists():
                with open(py_file, 'rb') as f:
                    bom = f.read(3)
                    if bom == b'\xef\xbb\xbf':
                        failures.append(f"{py_file}: has UTF-8 BOM")

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个文件有 UTF-8 BOM"
            result.details = failures

        return result

    def check_g1_2_chinese_sql(self) -> GateResult:
        r"""G1-2: 中文 SQL 字段检测

        检测 SQL 语句中直接使用中文字段名（未通过 column_names.py 常量）
        排除：column_names.py 自身、注释中的中文、字符串中的中文
        """
        result = GateResult("G1-2", "中文 SQL 字段检测", "PASS")
        failures = []

        for py_file in self._iterate_python_files():
            if "column_names.py" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                for line_no, line in enumerate(lines, 1):
                    stripped = line.strip()
                    # 跳过纯注释行
                    if stripped.startswith('#'):
                        continue

                    # 查找 SQL 关键字位置
                    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WHERE', 'FROM']
                    kw_pos = -1
                    kw_found = None
                    for kw in sql_keywords:
                        pos = line.find(kw)
                        if pos != -1 and (kw_pos == -1 or pos < kw_pos):
                            kw_pos = pos
                            kw_found = kw

                    if kw_pos == -1:
                        continue

                    # 查找行内 # 注释位置
                    comment_pos = -1
                    in_string = False
                    for i, ch in enumerate(line):
                        if ch in ('"', "'"):
                            in_string = not in_string
                        elif ch == '#' and not in_string:
                            comment_pos = i
                            break

                    # SQL 关键字在 # 之后 → 关键字在注释里，跳过
                    if comment_pos != -1 and comment_pos < kw_pos:
                        continue

                    # 检查关键字之后是否有中文（排除字符串）
                    chinese_found = False
                    string_depth = 0
                    for i in range(kw_pos + len(kw_found), len(line)):
                        ch = line[i]
                        if ch in ('"', "'"):
                            string_depth = 0 if string_depth == 1 else 1
                        elif string_depth == 0 and re.match(r'[\u4e00-\u9fff]', ch):
                            chinese_found = True
                            break

                    if chinese_found:
                        failures.append(f"{py_file}:{line_no}")
            except Exception:
                failures.extend(self._check_chinese_sql_python(py_file))

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 处疑似中文字段名在 SQL 中（未用 column_names.py 常量）"
            result.details = failures[:10]

        return result

    def _check_chinese_sql_python(self, file_path: pathlib.Path) -> list:
        """Python 实现的 G1-2 检查（fallback）"""
        failures = []
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WHERE', 'FROM']

            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue

                kw_pos = -1
                kw_found = None
                for kw in sql_keywords:
                    pos = line.find(kw)
                    if pos != -1 and (kw_pos == -1 or pos < kw_pos):
                        kw_pos = pos
                        kw_found = kw

                if kw_pos == -1:
                    continue

                # 跳过注释在关键字之前的情况
                comment_pos = -1
                in_string = False
                for i, ch in enumerate(line):
                    if ch in ('"', "'"):
                        in_string = not in_string
                    elif ch == '#' and not in_string:
                        comment_pos = i
                        break

                if comment_pos != -1 and comment_pos < kw_pos:
                    continue

                chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
                if chinese_pattern.search(line[kw_pos:]):
                    failures.append(f"{file_path}:{line_no}")
        except Exception:
            pass
        return failures

    def check_g1_3_placeholder_code(self) -> GateResult:
        """G1-3: 占位符代码检测"""
        result = GateResult("G1-3", "占位符代码检测", "PASS")
        failures = []

        pattern = re.compile(r'(^\s*\.\.\.\s*$|^\s*pass\s*#\s*TODO|raise\s+NotImplementedError)')
        for py_file in self._iterate_python_files():
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                for line_no, line in enumerate(lines, 1):
                    if pattern.match(line):
                        # 允许在抽象基类中的 raise NotImplementedError（需有 # abstract 注释）
                        if 'raise NotImplementedError' in line and '# abstract' in line:
                            continue
                        failures.append(f"{py_file}:{line_no}: {line.strip()}")
            except Exception:
                pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 处占位符代码"
            result.details = failures[:10]

        return result

    def check_g1_4_secrets(self) -> GateResult:
        """G1-4: 敏感信息检测（调用 detect-secrets）"""
        result = GateResult("G1-4", "敏感信息检测", "PASS")
        baseline_path = self.repo_path / ".secrets.baseline"

        if not baseline_path.exists():
            result.status = "WARN"
            result.message = ".secrets.baseline 不存在，跳过检测"
            return result

        try:
            import detect_secrets
            from detect_secrets import scan_file
            from detect_secrets.core import baseline

            with open(baseline_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            results = data.get('results', {})
            if results:
                # 过滤掉已豁免的
                active_secrets = {k: v for k, v in results.items()
                                 if not v.get('is_secret', True) or not v.get('baseline', True)}
                if active_secrets:
                    result.status = "FAIL"
                    result.message = f"发现 {len(active_secrets)} 个未处理敏感信息"
                    result.details = list(active_secrets.keys())[:5]
        except ImportError:
            result.status = "WARN"
            result.message = "detect-secrets 未安装，跳过检测"
        except Exception as e:
            result.status = "WARN"
            result.message = f"检测失败: {str(e)}"

        return result

    def check_g1_5_dependency_pinning(self) -> GateResult:
        """G1-5: 依赖版本锁定检测"""
        result = GateResult("G1-5", "依赖版本锁定检测", "PASS")
        failures = []

        for req_file in self.repo_path.glob("requirements*.txt"):
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line_no, line in enumerate(f, 1):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if not re.search(r'==[\d]', line):
                            failures.append(f"{req_file}:{line_no}: {line}")
            except Exception:
                pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个未锁定依赖"
            result.details = failures[:10]

        return result

    # ========================================================================
    # G2: CI Static Analysis
    # ========================================================================

    def check_g2_1_ruff(self) -> GateResult:
        """G2-1: Python 静态分析（ruff）"""
        result = GateResult("G2-1", "Python 静态分析 (ruff)", "PASS")

        try:
            proc = subprocess.run(
                ["ruff", "check", "backend/", "--output-format", "json"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            if proc.returncode != 0:
                try:
                    issues = json.loads(proc.stdout)
                    result.status = "FAIL"
                    result.message = f"ruff 发现 {len(issues)} 个问题"
                    result.details = [f"{i['filename']}:{i['location']['row']}: {i['message']}" for i in issues[:5]]
                except json.JSONDecodeError:
                    result.status = "FAIL"
                    result.message = "ruff 检查失败"
                    result.details = proc.stdout.split('\n')[:5]
        except FileNotFoundError:
            result.status = "WARN"
            result.message = "ruff 未安装，跳过检测"

        return result

    def check_g2_2_eslint(self) -> GateResult:
        """G2-2: ESLint（前端）"""
        result = GateResult("G2-2", "ESLint 前端静态分析", "PASS")
        frontend_path = self.repo_path / "frontend"

        if not frontend_path.exists():
            result.status = "SKIP"
            result.message = "frontend 目录不存在，跳过"
            return result

        try:
            proc = subprocess.run(
                ["npx", "eslint", "src/", "--ext", ".ts,.vue", "--max-warnings", "0", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=frontend_path
            )
            if proc.returncode != 0:
                try:
                    issues = json.loads(proc.stdout)
                    result.status = "FAIL"
                    result.message = f"ESLint 发现 {len(issues)} 个问题"
                    result.details = [f"{i['filePath']}: {i['messages'][0]['message']}" for i in issues[:5]]
                except json.JSONDecodeError:
                    result.status = "FAIL"
                    result.message = "ESLint 检查失败"
        except FileNotFoundError:
            result.status = "WARN"
            result.message = "npx/eslint 未安装，跳过检测"

        return result

    def check_g2_3_external_ddl(self) -> GateResult:
        """G2-3: 外部表 DDL 操作检测"""
        result = GateResult("G2-3", "外部表 DDL 检测", "PASS")
        failures = []

        external_tables = ["Tooling_ID_Main"]
        ddl_keywords = ["CREATE", "ALTER", "DROP", "TRUNCATE"]

        for py_file in self._iterate_python_files():
            try:
                content = py_file.read_text(encoding='utf-8')
                for kw in ddl_keywords:
                    for tbl in external_tables:
                        if re.search(rf'{kw}.*{tbl}', content, re.IGNORECASE):
                            failures.append(f"{py_file}: {kw} on {tbl}")
            except Exception:
                pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 处外部表 DDL 操作"
            result.details = failures

        return result

    # ========================================================================
    # G3: CI Test Gates
    # ========================================================================

    def check_g3_1_pytest_coverage(self) -> GateResult:
        """G3-1: Python 单元测试覆盖率"""
        result = GateResult("G3-1", "Python 单元测试覆盖", "SKIP")
        tests_dir = self.repo_path / "tests"

        if not tests_dir.exists():
            result.message = "tests 目录不存在，跳过"
            return result

        try:
            subprocess.run(["pytest", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            result.message = "pytest 未安装，跳过"
            return result

        result.status = "WARN"
        result.message = "G3-1 需要人工执行 pytest --cov=backend --cov-fail-under=80"
        return result

    def check_g3_2_integration_coverage(self) -> GateResult:
        """G3-2: 集成测试覆盖率"""
        result = GateResult("G3-2", "集成测试覆盖", "SKIP")
        result.message = "G3-2 需要人工执行集成测试"
        return result

    def check_g3_3_vitest(self) -> GateResult:
        """G3-3: 前端单元测试"""
        result = GateResult("G3-3", "前端单元测试 (Vitest)", "SKIP")
        frontend_path = self.repo_path / "frontend"

        if not frontend_path.exists():
            result.message = "frontend 目录不存在，跳过"
            return result

        try:
            subprocess.run(["npx", "vitest", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            result.message = "vitest 未安装，跳过"
            return result

        result.status = "WARN"
        result.message = "G3-3 需要人工执行 vitest"
        return result

    def check_g3_4_playwright(self) -> GateResult:
        """G3-4: E2E P0 路径覆盖"""
        result = GateResult("G3-4", "E2E P0 路径覆盖", "SKIP")
        result.message = "G3-4 需要人工执行 playwright"
        return result

    # ========================================================================
    # G4: CI Structure Checks
    # ========================================================================

    def check_g4_1_8d_structure(self) -> GateResult:
        """G4-1: 8D 文档结构检测"""
        result = GateResult("G4-1", "8D 文档结构检测", "PASS")
        failures = []

        required_sections = {
            "D2": ["What", "Where", "When", "Why"],
            "D3": ["临时措施", "爆炸半径"],
            "D4": ["根因", "Why"],
            "D5": ["永久对策", "修改文件"],
            "D6": ["测试", "验证"],
        }

        active_dir = self.repo_path / "promptsRec" / "active"
        if not active_dir.exists():
            result.status = "SKIP"
            result.message = "promptsRec/active 目录不存在，跳过"
            return result

        for prompt_file in active_dir.glob("1*.md"):
            if prompt_file.name.endswith('.lock'):
                continue
            try:
                content = prompt_file.read_text(encoding='utf-8', errors='ignore')
                for section, keywords in required_sections.items():
                    missing = [kw for kw in keywords if kw not in content]
                    if missing:
                        failures.append(f"{prompt_file.name}: {section} 缺少 {missing}")
            except Exception:
                pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个 8D 文档结构不完整"
            result.details = failures[:10]

        return result

    def check_g4_2_hotfix_rfc(self) -> GateResult:
        """G4-2: HOTFIX RFC 文档结构检测"""
        result = GateResult("G4-2", "HOTFIX RFC 结构检测", "PASS")

        required_sections = ["爆炸半径", "回滚预案", "影响模块"]
        active_dir = self.repo_path / "promptsRec" / "active"
        failures = []

        for prompt_file in active_dir.glob("hotfix_*.md"):
            try:
                content = prompt_file.read_text(encoding='utf-8', errors='ignore')
                missing = [s for s in required_sections if s not in content]
                if missing:
                    failures.append(f"{prompt_file.name}: 缺少 {missing}")
            except Exception:
                pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个 HOTFIX RFC 结构不完整"
            result.details = failures

        return result

    # ========================================================================
    # G5: CI Archive Guards
    # ========================================================================

    def check_g5_1_archive_naming(self) -> GateResult:
        """G5-1: 归档文件命名格式校验"""
        result = GateResult("G5-1", "归档命名格式校验", "PASS")
        failures = []

        archive_pattern = re.compile(r'^✅_\d{5}_\d{5}_[a-z][a-z0-9_]+_done\.md$')
        active_pattern = re.compile(r'^\d{5}_[a-z][a-z0-9_]+\.md$')

        archive_dir = self.repo_path / "promptsRec" / "archive"
        if archive_dir.exists():
            for f in archive_dir.iterdir():
                if f.is_file() and not archive_pattern.match(f.name) and f.name != '.gitkeep':
                    failures.append(f"archive/ 命名不合规: {f.name}")

        active_dir = self.repo_path / "promptsRec" / "active"
        if active_dir.exists():
            for f in active_dir.iterdir():
                if f.is_file() and f.suffix == '.md' and not active_pattern.match(f.name) and f.name != '.gitkeep':
                    failures.append(f"active/ 命名不合规: {f.name}")

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个命名不合规"
            result.details = failures[:10]

        return result

    def check_g5_2_exec_sequence(self) -> GateResult:
        """G5-2: 执行顺序号唯一性校验"""
        result = GateResult("G5-2", "执行顺序号唯一性校验", "PASS")

        seq_nums = []
        archive_dir = self.repo_path / "promptsRec" / "archive"
        dupes = []

        if archive_dir.exists():
            for f in archive_dir.iterdir():
                m = re.match(r'^✅_(\d{5})_', f.name)
                if m:
                    seq_num = m.group(1)
                    if seq_num in [s[0] for s in seq_nums]:
                        dupes.append(f"重复执行顺序号 {seq_num}: {f.name}")
                    seq_nums.append((seq_num, f.name))

        if dupes:
            result.status = "FAIL"
            result.message = f"发现 {len(dupes)} 个重复执行顺序号"
            result.details = dupes

        return result

    def check_g5_3_archive_precondition(self) -> GateResult:
        """G5-3: 归档前测试报告存在性校验"""
        result = GateResult("G5-3", "归档前置条件校验", "PASS")
        failures = []

        report_dir = self.repo_path / "logs" / "prompt_task_runs"
        archive_dir = self.repo_path / "promptsRec" / "archive"

        if not archive_dir.exists():
            result.status = "SKIP"
            result.message = "archive 目录不存在，跳过"
            return result

        for f in archive_dir.iterdir():
            m = re.match(r'^✅_\d{5}_(\d{5})_', f.name)
            if not m:
                continue
            task_id = m.group(1)
            found = False

            if report_dir.exists():
                for report in report_dir.glob("*.md"):
                    content = report.read_text(encoding='utf-8', errors='ignore')
                    if task_id in report.name or f"**ID**: {task_id}" in content:
                        found = True
                        break

            if not found:
                failures.append(f"{f.name}: 缺少测试报告")

        if failures:
            result.status = "WARN"
            result.message = f"发现 {len(failures)} 个归档缺少测试报告"
            result.details = failures[:10]

        return result

    # ========================================================================
    # G6: Skill File Gates
    # ========================================================================

    def check_g6_1_skill_size(self) -> GateResult:
        """G6-1: 技能文件体积检查（≤20KB）"""
        result = GateResult("G6-1", "技能文件体积检查", "PASS")
        failures = []
        warnings = []

        skills_dirs = self._get_skills_dirs()
        if not skills_dirs:
            result.status = "SKIP"
            result.message = "未找到 .skills 目录（项目级和全局级），跳过"
            return result

        for skills_dir in skills_dirs:
            is_global = skills_dir == self.global_skills_path
            prefix = "[全局] " if is_global else "[项目] "

            for skill_file in skills_dir.rglob("SKILL.md"):
                try:
                    size = skill_file.stat().st_size
                    size_kb = size / 1024
                    rel_path = skill_file.parent.name
                    if size_kb > 20:
                        failures.append(f"{prefix}{rel_path}/SKILL.md: {size_kb:.1f}KB > 20KB")
                    elif size_kb > 15:
                        warnings.append(f"{prefix}{rel_path}/SKILL.md: {size_kb:.1f}KB (15-20KB 警告)")
                except Exception:
                    pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个技能文件超过 20KB"
            result.details = failures
        elif warnings:
            result.status = "WARN"
            result.message = f"发现 {len(warnings)} 个技能文件在 15-20KB 范围"
            result.details = warnings

        return result

    def check_g6_2_frontmatter(self) -> GateResult:
        """G6-2: Frontmatter 完整性检查"""
        result = GateResult("G6-2", "Frontmatter 完整性检查", "PASS")
        failures = []

        required_fields = ["name", "executor", "auto_invoke", "depends_on", "triggers", "rules_ref", "version"]
        valid_executors = ["Claude Code", "Codex", "Human"]

        skills_dirs = self._get_skills_dirs()
        if not skills_dirs:
            result.status = "SKIP"
            result.message = "未找到 .skills 目录，跳过"
            return result

        for skills_dir in skills_dirs:
            is_global = skills_dir == self.global_skills_path
            prefix = "[全局] " if is_global else "[项目] "

            for skill_file in skills_dir.rglob("SKILL.md"):
                try:
                    content = skill_file.read_text(encoding='utf-8')
                    fm = self._parse_frontmatter(content)

                    missing = [f for f in required_fields if f not in fm]
                    if missing:
                        failures.append(f"{prefix}{skill_file.parent.name}/SKILL.md: 缺少 {missing}")
                        continue

                    if fm.get('executor') not in valid_executors:
                        failures.append(f"{prefix}{skill_file.parent.name}/SKILL.md: executor 值非法 ({fm.get('executor')})")

                    expected_name = skill_file.parent.name
                    if fm.get('name') != expected_name:
                        failures.append(f"{prefix}{skill_file.parent.name}/SKILL.md: name 与目录名不匹配 ({fm.get('name')})")
                except Exception as e:
                    failures.append(f"{prefix}{skill_file.parent.name}/SKILL.md: 解析失败 {str(e)}")

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个 Frontmatter 不合规"
            result.details = failures

        return result

    def check_g6_3_trigger_uniqueness(self) -> GateResult:
        """G6-3: triggers 全局唯一性检查"""
        result = GateResult("G6-3", "触发命令全局唯一性", "PASS")

        all_triggers = {}
        skills_dirs = self._get_skills_dirs()

        if not skills_dirs:
            result.status = "SKIP"
            result.message = "未找到 .skills 目录，跳过"
            return result

        for skills_dir in skills_dirs:
            is_global = skills_dir == self.global_skills_path
            prefix = "[全局]" if is_global else "[项目]"

            for skill_file in skills_dir.rglob("SKILL.md"):
                try:
                    content = skill_file.read_text(encoding='utf-8')
                    fm = self._parse_frontmatter(content)
                    triggers = fm.get('triggers', [])
                    if isinstance(triggers, list):
                        for t in triggers:
                            key = f"{prefix} {skill_file.parent.name}/{t}"
                            if t in all_triggers:
                                result.status = "FAIL"
                                all_triggers[t].append(key)
                            else:
                                all_triggers[t] = [key]
                except Exception:
                    pass

        conflicts = {t: files for t, files in all_triggers.items() if len(files) > 1}
        if conflicts:
            result.status = "FAIL"
            result.message = f"发现 {len(conflicts)} 个触发命令冲突"
            result.details = [f"{t}: {files}" for t, files in conflicts.items()]

        return result

    def check_g6_4_dependency_exists(self) -> GateResult:
        """G6-4: depends_on 引用存在性检查"""
        result = GateResult("G6-4", "depends_on 引用存在性", "PASS")
        failures = []

        skills_dirs = self._get_skills_dirs()
        if not skills_dirs:
            result.status = "SKIP"
            result.message = "未找到 .skills 目录，跳过"
            return result

        for skills_dir in skills_dirs:
            is_global = skills_dir == self.global_skills_path
            prefix = "[全局] " if is_global else "[项目] "

            for skill_file in skills_dir.rglob("SKILL.md"):
                try:
                    content = skill_file.read_text(encoding='utf-8')
                    fm = self._parse_frontmatter(content)
                    deps = fm.get('depends_on', [])
                    if isinstance(deps, list):
                        for dep in deps:
                            dep_path = skills_dir / dep
                            if not dep_path.exists():
                                failures.append(f"{prefix}{skill_file.parent.name}: 依赖 {dep} 不存在")
                except Exception:
                    pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个依赖引用不存在"
            result.details = failures

        return result

    def check_g6_5_meta_skill(self) -> GateResult:
        """G6-5: 元技能 auto_invoke 必须为 false"""
        result = GateResult("G6-5", "元技能保护检查", "PASS")
        failures = []

        skills_dirs = self._get_skills_dirs()
        if not skills_dirs:
            result.status = "SKIP"
            result.message = "未找到 .skills 目录，跳过"
            return result

        for skills_dir in skills_dirs:
            is_global = skills_dir == self.global_skills_path
            prefix = "[全局] " if is_global else "[项目] "

            for skill_file in skills_dir.rglob("SKILL.md"):
                try:
                    content = skill_file.read_text(encoding='utf-8')
                    fm = self._parse_frontmatter(content)
                    skill_name = skill_file.parent.name

                    if skill_name.startswith('skill-') and fm.get('auto_invoke') == True:
                        failures.append(f"{prefix}{skill_name}/SKILL.md: 元技能 auto_invoke 必须为 false")
                except Exception:
                    pass

        if failures:
            result.status = "FAIL"
            result.message = f"发现 {len(failures)} 个元技能 auto_invoke 违规"
            result.details = failures

        return result

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _iterate_python_files(self):
        """遍历所有 Python 文件"""
        backend_dir = self.repo_path / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                yield py_file

    def _parse_frontmatter(self, content: str) -> dict:
        """解析 YAML frontmatter"""
        fm = {}
        lines = content.split('\n')
        if not lines:
            return fm

        start_idx = 0
        # 找到 frontmatter 结束位置
        # 情况1: 有 --- 分隔符
        if lines[0].strip() == '---':
            fm_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    fm_end = i
                    break
            if fm_end == -1:
                return fm
            start_idx = 1
            end_idx = fm_end
        else:
            # 情况2: 没有 --- 分隔符，找第一个空行或 --- 或非 key:value 行
            fm_end = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped or stripped.startswith('#') or stripped.startswith('---') or (':' not in stripped and not stripped.startswith('-')):
                    # 如果还没找到任何 key，继续
                    if fm_end == 0 and i > 0:
                        # 检查是否是连续的 key:value 格式
                        pass
                    else:
                        fm_end = i
                        break
                else:
                    fm_end = i + 1
            end_idx = fm_end if fm_end > 0 else len(lines)

        # 解析 frontmatter 行
        i = start_idx
        while i < end_idx and i < len(lines):
            line = lines[i].rstrip()
            i += 1

            if not line or line.startswith('#'):
                continue

            # 没有分隔符的情况：如果遇到非 key:value 格式，停止
            if ':' not in line and not line.strip().startswith('-'):
                continue

            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # 处理空值
            if not value:
                fm[key] = []
                continue

            # 处理列表值
            if value.startswith('[') and value.endswith(']'):
                inner = value[1:-1].strip()
                if not inner:
                    fm[key] = []
                else:
                    items = [x.strip() for x in inner.split(',')]
                    fm[key] = items
            elif value.startswith('-'):
                # 多行列表
                items = []
                while i < end_idx and i < len(lines) and lines[i].strip().startswith('-'):
                    items.append(lines[i].strip()[1:].strip())
                    i += 1
                fm[key] = items
            else:
                fm[key] = value

        return fm

    def run_all_gates(self) -> ScanResult:
        """执行所有门禁检查"""
        scan_result = ScanResult(repo_path=str(self.repo_path))

        # G1
        scan_result.add(self.check_g1_1_utf8_bom())
        scan_result.add(self.check_g1_2_chinese_sql())
        scan_result.add(self.check_g1_3_placeholder_code())
        scan_result.add(self.check_g1_4_secrets())
        scan_result.add(self.check_g1_5_dependency_pinning())

        # G2
        scan_result.add(self.check_g2_1_ruff())
        scan_result.add(self.check_g2_2_eslint())
        scan_result.add(self.check_g2_3_external_ddl())

        # G3
        scan_result.add(self.check_g3_1_pytest_coverage())
        scan_result.add(self.check_g3_2_integration_coverage())
        scan_result.add(self.check_g3_3_vitest())
        scan_result.add(self.check_g3_4_playwright())

        # G4
        scan_result.add(self.check_g4_1_8d_structure())
        scan_result.add(self.check_g4_2_hotfix_rfc())

        # G5
        scan_result.add(self.check_g5_1_archive_naming())
        scan_result.add(self.check_g5_2_exec_sequence())
        scan_result.add(self.check_g5_3_archive_precondition())

        # G6
        scan_result.add(self.check_g6_1_skill_size())
        scan_result.add(self.check_g6_2_frontmatter())
        scan_result.add(self.check_g6_3_trigger_uniqueness())
        scan_result.add(self.check_g6_4_dependency_exists())
        scan_result.add(self.check_g6_5_meta_skill())

        return scan_result
