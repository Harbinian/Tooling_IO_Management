# -*- coding: utf-8 -*-
"""Repository for detachable component MPL groups."""

from __future__ import annotations

from typing import Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import MPL_COLUMNS, TABLE_NAMES


class MplRepository:
    """Persist MPL groups as one row per detachable component."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    @staticmethod
    def build_mpl_no(tool_drawing_no: str, tool_revision: str) -> str:
        drawing = str(tool_drawing_no or "").strip()
        revision = str(tool_revision or "").strip() or "NA"
        return f"MPL-{drawing}-{revision}"

    def get_by_tool(self, tool_drawing_no: str, tool_revision: str) -> List[Dict]:
        return self._db.execute_query(
            f"""
            SELECT
                [{MPL_COLUMNS['id']}] AS id,
                [{MPL_COLUMNS['mpl_no']}] AS mpl_no,
                [{MPL_COLUMNS['tool_drawing_no']}] AS tool_drawing_no,
                [{MPL_COLUMNS['tool_revision']}] AS tool_revision,
                [{MPL_COLUMNS['component_no']}] AS component_no,
                [{MPL_COLUMNS['component_name']}] AS component_name,
                [{MPL_COLUMNS['quantity']}] AS quantity,
                [{MPL_COLUMNS['photo_data']}] AS photo_data,
                [{MPL_COLUMNS['created_by']}] AS created_by,
                [{MPL_COLUMNS['created_at']}] AS created_at,
                [{MPL_COLUMNS['updated_at']}] AS updated_at
            FROM [{TABLE_NAMES['MPL']}]
            WHERE [{MPL_COLUMNS['tool_drawing_no']}] = ?
              AND [{MPL_COLUMNS['tool_revision']}] = ?
            ORDER BY [{MPL_COLUMNS['component_no']}], [{MPL_COLUMNS['id']}]
            """,
            (str(tool_drawing_no or "").strip(), str(tool_revision or "").strip()),
        )

    def get_by_mpl_no(self, mpl_no: str) -> List[Dict]:
        return self._db.execute_query(
            f"""
            SELECT
                [{MPL_COLUMNS['id']}] AS id,
                [{MPL_COLUMNS['mpl_no']}] AS mpl_no,
                [{MPL_COLUMNS['tool_drawing_no']}] AS tool_drawing_no,
                [{MPL_COLUMNS['tool_revision']}] AS tool_revision,
                [{MPL_COLUMNS['component_no']}] AS component_no,
                [{MPL_COLUMNS['component_name']}] AS component_name,
                [{MPL_COLUMNS['quantity']}] AS quantity,
                [{MPL_COLUMNS['photo_data']}] AS photo_data,
                [{MPL_COLUMNS['created_by']}] AS created_by,
                [{MPL_COLUMNS['created_at']}] AS created_at,
                [{MPL_COLUMNS['updated_at']}] AS updated_at
            FROM [{TABLE_NAMES['MPL']}]
            WHERE [{MPL_COLUMNS['mpl_no']}] = ?
            ORDER BY [{MPL_COLUMNS['component_no']}], [{MPL_COLUMNS['id']}]
            """,
            (str(mpl_no or "").strip(),),
        )

    def mpl_exists(self, tool_drawing_no: str, tool_revision: str) -> bool:
        rows = self._db.execute_query(
            f"""
            SELECT TOP 1 1 AS existing_flag
            FROM [{TABLE_NAMES['MPL']}]
            WHERE [{MPL_COLUMNS['tool_drawing_no']}] = ?
              AND [{MPL_COLUMNS['tool_revision']}] = ?
            """,
            (str(tool_drawing_no or "").strip(), str(tool_revision or "").strip()),
        )
        return bool(rows)

    def create_mpl(self, mpl_data: Dict) -> Dict:
        mpl_no = self.build_mpl_no(mpl_data.get("tool_drawing_no", ""), mpl_data.get("tool_revision", ""))
        self._replace_group(mpl_no, mpl_data)
        return self.get_group(mpl_no) or {}

    def update_mpl(self, mpl_no: str, mpl_data: Dict) -> Dict:
        normalized_no = str(mpl_no or "").strip()
        if not normalized_no:
            return {}
        self._replace_group(normalized_no, mpl_data)
        return self.get_group(normalized_no) or {}

    def delete_mpl(self, mpl_no: str) -> bool:
        self._db.execute_query(
            f"DELETE FROM [{TABLE_NAMES['MPL']}] WHERE [{MPL_COLUMNS['mpl_no']}] = ?",
            (str(mpl_no or "").strip(),),
            fetch=False,
        )
        return True

    def list_all(self, page: int, page_size: int, drawing_no: str = "", keyword: str = "") -> Dict:
        page_no = max(int(page or 1), 1)
        page_size = max(int(page_size or 20), 1)
        offset = (page_no - 1) * page_size

        conditions = ["1=1"]
        params: List[object] = []
        normalized_drawing = str(drawing_no or "").strip()
        normalized_keyword = str(keyword or "").strip()

        if normalized_drawing:
            conditions.append(f"base.[{MPL_COLUMNS['tool_drawing_no']}] LIKE ?")
            params.append(f"%{normalized_drawing}%")
        if normalized_keyword:
            conditions.append(
                f"""(
                    base.[{MPL_COLUMNS['tool_drawing_no']}] LIKE ?
                    OR base.[{MPL_COLUMNS['tool_revision']}] LIKE ?
                    OR base.[{MPL_COLUMNS['component_no']}] LIKE ?
                    OR base.[{MPL_COLUMNS['component_name']}] LIKE ?
                )"""
            )
            params.extend([f"%{normalized_keyword}%"] * 4)

        where_clause = " AND ".join(conditions)
        total_rows = self._db.execute_query(
            f"""
            SELECT COUNT(1) AS total
            FROM (
                SELECT DISTINCT [{MPL_COLUMNS['mpl_no']}]
                FROM [{TABLE_NAMES['MPL']}] AS base
                WHERE {where_clause}
            ) AS grouped
            """,
            tuple(params),
        )
        total = int((total_rows[0] if total_rows else {}).get("total", 0))

        rows = self._db.execute_query(
            f"""
            WITH grouped AS (
                SELECT
                    base.[{MPL_COLUMNS['mpl_no']}] AS mpl_no,
                    MIN(base.[{MPL_COLUMNS['tool_drawing_no']}]) AS tool_drawing_no,
                    MIN(base.[{MPL_COLUMNS['tool_revision']}]) AS tool_revision,
                    COUNT(1) AS component_count,
                    MAX(base.[{MPL_COLUMNS['updated_at']}]) AS updated_at
                FROM [{TABLE_NAMES['MPL']}] AS base
                WHERE {where_clause}
                GROUP BY base.[{MPL_COLUMNS['mpl_no']}]
            )
            SELECT
                mpl_no,
                tool_drawing_no,
                tool_revision,
                component_count,
                updated_at
            FROM grouped
            ORDER BY updated_at DESC, mpl_no DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """,
            tuple(params + [offset, page_size]),
        )
        return {"data": rows, "total": total, "page_no": page_no, "page_size": page_size}

    def get_group(self, mpl_no: str) -> Optional[Dict]:
        rows = self.get_by_mpl_no(mpl_no)
        if not rows:
            return None
        first = rows[0]
        return {
            "mpl_no": first.get("mpl_no", ""),
            "tool_drawing_no": first.get("tool_drawing_no", ""),
            "tool_revision": first.get("tool_revision", ""),
            "items": rows,
            "component_count": len(rows),
            "updated_at": max((row.get("updated_at") for row in rows), default=None),
        }

    def _replace_group(self, mpl_no: str, mpl_data: Dict) -> None:
        tool_drawing_no = str(mpl_data.get("tool_drawing_no", "")).strip()
        tool_revision = str(mpl_data.get("tool_revision", "")).strip()
        created_by = str(mpl_data.get("created_by") or mpl_data.get("updated_by") or "").strip() or "system"
        items = mpl_data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError("items must contain at least one component")

        conn = self._db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"DELETE FROM [{TABLE_NAMES['MPL']}] WHERE [{MPL_COLUMNS['mpl_no']}] = ?",
                (mpl_no,),
            )
            insert_sql = f"""
            INSERT INTO [{TABLE_NAMES['MPL']}] (
                [{MPL_COLUMNS['mpl_no']}],
                [{MPL_COLUMNS['tool_drawing_no']}],
                [{MPL_COLUMNS['tool_revision']}],
                [{MPL_COLUMNS['component_no']}],
                [{MPL_COLUMNS['component_name']}],
                [{MPL_COLUMNS['quantity']}],
                [{MPL_COLUMNS['photo_data']}],
                [{MPL_COLUMNS['created_by']}],
                [{MPL_COLUMNS['created_at']}],
                [{MPL_COLUMNS['updated_at']}]
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), SYSDATETIME())
            """
            for item in items:
                cursor.execute(
                    insert_sql,
                    (
                        mpl_no,
                        tool_drawing_no,
                        tool_revision,
                        str(item.get("component_no", "")).strip(),
                        str(item.get("component_name", "")).strip(),
                        int(item.get("quantity", 1) or 1),
                        item.get("photo_data"),
                        created_by,
                    ),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            self._db.close(conn)
