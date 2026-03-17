# -*- coding: utf-8 -*-
"""
Debug SQL parser - print all parsed statements
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_sql_file(sql_file_path):
    """Parse SQL file into individual statements"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    statements = []
    current_stmt = []
    in_multiline_comment = False

    for line_num, line in enumerate(content.split('\n'), 1):
        stripped = line.strip()

        # Skip single-line comments
        if stripped.startswith('--'):
            continue

        # Handle multiline comments
        if '/*' in stripped:
            in_multiline_comment = True
        if in_multiline_comment:
            if '*/' in stripped:
                in_multiline_comment = False
            continue

        current_stmt.append(line)

        # End statement on semicolon
        if stripped.endswith(';'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt and not stmt.startswith('/*'):
                statements.append((line_num, stmt))
            current_stmt = []

    return statements


def main():
    sql_file = os.path.join(
        os.path.dirname(__file__),
        '001_rename_tables_to_english.sql'
    )

    statements = parse_sql_file(sql_file)
    print(f"Parsed {len(statements)} statements\n")

    for i, (line_num, stmt) in enumerate(statements, 1):
        preview = stmt[:100].replace('\n', ' ')
        if len(stmt) > 100:
            preview += '...'
        print(f"[{i:3d}] (line ~{line_num}) {preview}\n")

        # Check for issues
        if 'sp_rename' in stmt:
            print("    [CONTAINS sp_rename]")
        if 'INTO' in stmt.upper():
            print("    [CONTAINS INTO]")


if __name__ == "__main__":
    main()
