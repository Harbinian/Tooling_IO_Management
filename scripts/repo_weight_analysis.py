#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Weight Analysis Script

Analyzes repository to identify:
- Largest files
- Files with most lines
- Heaviest directories
- File type distribution
- AI context hotspots
- Optimization candidates
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Configuration
ROOT_DIR = Path(__file__).parent.parent.resolve()
IGNORE_DIRS = {
    '.git', 'node_modules', '.venv', 'venv', '__pycache__',
    '.pytest_cache', '.mypy_cache', 'dist', 'build', '.ruff_cache',
    'frontend/dist', 'frontend/node_modules'
}
IGNORE_EXTENSIONS = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin'}
MAX_LINE_COUNT = 400
MAX_FILE_SIZE_KB = 50
MAX_MD_SIZE_KB = 20


def get_all_files(root: Path) -> list[Path]:
    """Get all files in repository, excluding ignored directories."""
    files = []
    for item in root.rglob('*'):
        if item.is_file():
            # Check if any parent is ignored
            if any(ignored in item.parts for ignored in IGNORE_DIRS):
                continue
            # Check extension
            if item.suffix.lower() in IGNORE_EXTENSIONS:
                continue
            files.append(item)
    return files


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    try:
        return file_path.stat().st_size
    except (OSError, PermissionError):
        return 0


def count_lines(file_path: Path) -> int:
    """Count lines in a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except (OSError, PermissionError):
        return 0


def is_text_file(file_path: Path) -> bool:
    """Check if file is a text file based on extension."""
    text_extensions = {
        '.py', '.js', '.ts', '.vue', '.jsx', '.tsx', '.md',
        '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
        '.html', '.css', '.scss', '.sass', '.less',
        '.sh', '.bat', '.ps1', '.sql', '.xml'
    }
    return file_path.suffix.lower() in text_extensions


def analyze_files(files: list[Path]) -> dict:
    """Analyze all files and return metrics."""
    file_data = []
    for f in files:
        size = get_file_size(f)
        lines = count_lines(f) if is_text_file(f) else 0
        rel_path = f.relative_to(ROOT_DIR)
        file_data.append({
            'path': rel_path,
            'size': size,
            'lines': lines,
            'extension': f.suffix.lower()
        })
    return file_data


def get_largest_files(file_data: list[dict], n: int = 20) -> list[dict]:
    """Get top N largest files by size."""
    return sorted(file_data, key=lambda x: x['size'], reverse=True)[:n]


def get_most_lines(file_data: list[dict], n: int = 20) -> list[dict]:
    """Get top N files by line count."""
    text_files = [f for f in file_data if f['lines'] > 0]
    return sorted(text_files, key=lambda x: x['lines'], reverse=True)[:n]


def get_directory_weight(file_data: list[dict]) -> dict:
    """Aggregate metrics by directory."""
    dir_metrics = defaultdict(lambda: {'files': 0, 'size': 0, 'lines': 0})

    for f in file_data:
        parts = f['path'].parts
        if len(parts) > 1:
            # Top-level directory
            top_dir = parts[0]
            dir_metrics[top_dir]['files'] += 1
            dir_metrics[top_dir]['size'] += f['size']
            dir_metrics[top_dir]['lines'] += f['lines']

    return dict(dir_metrics)


def get_file_type_distribution(file_data: list[dict]) -> dict:
    """Get distribution by file extension."""
    type_metrics = defaultdict(lambda: {'count': 0, 'size': 0})

    for f in file_data:
        ext = f['extension'] or '(no extension)'
        type_metrics[ext]['count'] += 1
        type_metrics[ext]['size'] += f['size']

    return dict(type_metrics)


def get_context_hotspots(file_data: list[dict]) -> list[dict]:
    """Identify files likely to cause AI context issues."""
    hotspots = []

    for f in file_data:
        size_kb = f['size'] / 1024
        reasons = []

        if f['lines'] > MAX_LINE_COUNT:
            reasons.append(f"lines={f['lines']}")

        if size_kb > MAX_FILE_SIZE_KB:
            reasons.append(f"size={size_kb:.1f}KB")

        if f['extension'] == '.md' and size_kb > MAX_MD_SIZE_KB:
            reasons.append(f"md_size={size_kb:.1f}KB")

        # Check for generated/archived files
        path_str = str(f['path'])
        if '✅_' in path_str or 'archive' in path_str.lower():
            reasons.append("archived")
        if 'logs' in path_str.lower() or 'review' in path_str.lower():
            reasons.append("generated/report")

        if reasons:
            hotspots.append({
                'path': f['path'],
                'size': f['size'],
                'lines': f['lines'],
                'reasons': reasons
            })

    return sorted(hotspots, key=lambda x: x['size'], reverse=True)


def get_optimization_candidates(file_data: list[dict]) -> dict:
    """Identify candidates for optimization."""
    # Split candidates: large source files
    split_candidates = []
    for f in file_data:
        if f['lines'] > 500 and f['extension'] in ['.py', '.js', '.ts', '.vue']:
            split_candidates.append({
                'path': f['path'],
                'lines': f['lines']
            })

    # Ignore candidates
    ignore_candidates = [
        'logs/',
        'review-reports/',
        'promptsRec/✅_',
        'frontend/node_modules/',
        'frontend/dist/',
        '__pycache__/',
        '.venv/'
    ]

    # Archive candidates
    archive_candidates = [f for f in file_data if '✅_' in str(f['path'])]

    return {
        'split_candidates': sorted(split_candidates, key=lambda x: x['lines'], reverse=True)[:10],
        'ignore_candidates': ignore_candidates,
        'archive_count': len(archive_candidates)
    }


def generate_report(file_data: list[dict]) -> str:
    """Generate markdown report."""
    lines = []

    lines.append("# Repository Weight Analysis Report\n")
    lines.append(f"**Generated:** Analysis of repository at `{ROOT_DIR}`\n")

    # Summary
    total_size = sum(f['size'] for f in file_data)
    total_lines = sum(f['lines'] for f in file_data)
    lines.append("## Summary\n")
    lines.append(f"- **Total Files:** {len(file_data):,}")
    lines.append(f"- **Total Size:** {total_size / 1024 / 1024:.2f} MB")
    lines.append(f"- **Total Lines (text):** {total_lines:,}\n")

    # Largest files
    largest = get_largest_files(file_data, 15)
    lines.append("## Top 15 Largest Files\n")
    lines.append("| Size | Lines | Path |")
    lines.append("|------|-------|------|")
    for f in largest:
        size_kb = f['size'] / 1024
        lines.append(f"| {size_kb:.1f} KB | {f['lines']:,} | {f['path']} |")
    lines.append("")

    # Most lines
    most_lines = get_most_lines(file_data, 15)
    lines.append("## Top 15 Files by Line Count\n")
    lines.append("| Lines | Size | Path |")
    lines.append("|-------|------|------|")
    for f in most_lines:
        size_kb = f['size'] / 1024
        lines.append(f"| {f['lines']:,} | {size_kb:.1f} KB | {f['path']} |")
    lines.append("")

    # Directory weight
    dir_weight = get_directory_weight(file_data)
    sorted_dirs = sorted(dir_weight.items(), key=lambda x: x[1]['size'], reverse=True)
    lines.append("## Directory Weight\n")
    lines.append("| Directory | Files | Size | Lines |")
    lines.append("|----------|-------|------|-------|")
    for dir_name, metrics in sorted_dirs:
        size_mb = metrics['size'] / 1024 / 1024
        lines.append(f"| {dir_name} | {metrics['files']:,} | {size_mb:.2f} MB | {metrics['lines']:,} |")
    lines.append("")

    # File type distribution
    type_dist = get_file_type_distribution(file_data)
    sorted_types = sorted(type_dist.items(), key=lambda x: x[1]['size'], reverse=True)
    lines.append("## File Type Distribution\n")
    lines.append("| Extension | Count | Total Size |")
    lines.append("|----------|-------|------------|")
    for ext, metrics in sorted_types[:15]:
        size_kb = metrics['size'] / 1024
        lines.append(f"| {ext} | {metrics['count']:,} | {size_kb:.1f} KB |")
    lines.append("")

    # Context hotspots
    hotspots = get_context_hotspots(file_data)
    lines.append("## AI Context Hotspots\n")
    lines.append("Files that may cause token bloat:\n")
    lines.append("| Size | Lines | Reasons | Path |")
    lines.append("|------|-------|---------|------|")
    for h in hotspots[:20]:
        size_kb = h['size'] / 1024
        reasons = ', '.join(h['reasons'])
        lines.append(f"| {size_kb:.1f} KB | {h['lines']:,} | {reasons} | {h['path']} |")
    lines.append("")

    # Optimization candidates
    opt = get_optimization_candidates(file_data)
    lines.append("## Optimization Candidates\n")
    lines.append("### Split Candidates (large source files)\n")
    for c in opt['split_candidates'][:10]:
        lines.append(f"- {c['path']} ({c['lines']} lines)")
    lines.append("")

    lines.append("### Ignore Candidates\n")
    for c in opt['ignore_candidates']:
        lines.append(f"- {c}")
    lines.append("")

    lines.append(f"### Archive Candidates\n")
    lines.append(f"- {opt['archive_count']} archived prompt files\n")

    return '\n'.join(lines)


def main():
    print(f"Analyzing repository: {ROOT_DIR}")

    # Get all files
    files = get_all_files(ROOT_DIR)
    print(f"Found {len(files)} files")

    # Analyze
    file_data = analyze_files(files)

    # Generate report
    report = generate_report(file_data)

    # Write report
    report_path = ROOT_DIR / 'analysis' / 'repo_weight_report.md'
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report generated: {report_path}")

    # Print summary
    total_size = sum(f['size'] for f in file_data)
    hotspots = get_context_hotspots(file_data)
    print(f"\nSummary:")
    print(f"  Total files: {len(file_data)}")
    print(f"  Total size: {total_size / 1024 / 1024:.2f} MB")
    print(f"  Context hotspots: {len(hotspots)}")


if __name__ == '__main__':
    main()
