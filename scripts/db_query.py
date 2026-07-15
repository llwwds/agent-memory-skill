# db_query.py -- Memory query and tag pool tool
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_utils import (DB_FILES, get_conn, now_iso, is_multi_value,
                       deserialize_multi, output_json)

SKIP_COLS = {"__table__"}

TEXT_COLS = {
    "conversations": ["content", "summary"],
    "events": ["overview", "name"],
    "persona": ["content", "key"],
    "tools": ["overview", "usage_guide", "tech_manual", "name"],
}

def list_tags(db_name, column_name):
    conn = get_conn(db_name)
    rows = conn.execute(
        "SELECT DISTINCT tag_value FROM _tag_pool WHERE column_name = ? ORDER BY usage_count DESC",
        (column_name,)
    ).fetchall()
    conn.close()
    tags = [r["tag_value"] for r in rows]
    print(json.dumps(tags, ensure_ascii=False))

def list_all_tag_columns(db_name):
    conn = get_conn(db_name)
    rows = conn.execute(
        "SELECT column_name, COUNT(*) as cnt FROM _tag_pool GROUP BY column_name ORDER BY column_name"
    ).fetchall()
    conn.close()
    result = {r["column_name"]: r["cnt"] for r in rows}
    print(json.dumps(result, ensure_ascii=False))

def query_rows(db_name, filters, order_by, limit, offset, content_like=None):
    conn = get_conn(db_name)
    where_parts = []
    params = []

    if content_like:
        text_cols = TEXT_COLS[db_name]
        where_parts.append("(" + " OR ".join(f"{col} LIKE ?" for col in text_cols) + ")")
        like_val = f"%{content_like}%"
        params.extend([like_val] * len(text_cols))

    for col, val in filters.items():
        if col in SKIP_COLS:
            continue
        if is_multi_value(db_name, col):
            where_parts.append(f"({col} LIKE ?)")
            params.append(f"%{val}%")
        else:
            where_parts.append(f"{col} = ?")
            params.append(val)

    where_clause = ""
    if where_parts:
        AND = " AND "
        where_clause = "WHERE " + AND.join(where_parts)

    order_clause = ""
    if order_by:
        safe_order = order_by.replace(";", "").replace("--", "")
        order_clause = f"ORDER BY {safe_order} DESC"

    limit_clause = ""
    params_list = list(params)
    if limit:
        limit_clause = "LIMIT ?"
        params_list.append(int(limit))
    if offset:
        limit_clause += " OFFSET ?"
        params_list.append(int(offset))

    sql = f"SELECT * FROM {db_name} {where_clause} {order_clause} {limit_clause}"
    rows = conn.execute(sql, params_list).fetchall()
    conn.close()
    print(output_json(rows, db_name))

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Memory query tool")
    p.add_argument("--db", required=True, choices=list(DB_FILES.keys()))
    p.add_argument("--list-tags", action="store_true")
    p.add_argument("--column", help="Column name for --list-tags")
    p.add_argument("--content-like", help="Search content/summary/overview")
    p.add_argument("--event", help="Filter by event tag")
    p.add_argument("--device", help="Filter by device")
    p.add_argument("--deployment", help="Filter by deployment")
    p.add_argument("--status", help="Filter by status")
    p.add_argument("--name", help="Filter by name")
    p.add_argument("--section", help="Filter by section")
    p.add_argument("--key", help="Filter by key")
    p.add_argument("--order-by", default="created_at")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    if a.list_tags:
        if not a.column:
            list_all_tag_columns(a.db)
        else:
            list_tags(a.db, a.column)
        sys.exit(0)

    filters = {}
    if a.event: filters["event"] = a.event
    if a.device: filters["device"] = a.device
    if a.deployment: filters["deployment"] = a.deployment
    if a.status: filters["status"] = a.status
    if a.name: filters["name"] = a.name
    if a.section: filters["section"] = a.section
    if a.key: filters["key"] = a.key

    query_rows(a.db, filters, a.order_by, a.limit, a.offset, a.content_like)
