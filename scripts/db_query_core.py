# db_query_core.py -- Shared query logic for all search scripts
import json
from db_utils import (get_conn, is_multi_value, output_json)

SKIP_COLS = {"__table__"}

TEXT_COLS = {
    "conversations": ["content", "summary"],
    "events": ["overview", "name"],
    "persona": ["content", "key"],
    "tools": ["overview", "usage_guide", "tech_manual", "name"],
}

def query_rows(db_name, filters, order_by=None, limit=50, offset=0, content_like=None):
    conn = get_conn(db_name)
    where_parts = []
    params = []

    if content_like:
        cols = TEXT_COLS.get(db_name, ["content"])
        parts = " OR ".join(["{0} LIKE ?".format(c) for c in cols])
        where_parts.append("({0})".format(parts))
        like_val = "%" + content_like + "%"
        params.extend([like_val] * len(cols))

    for col, val in filters.items():
        if col in SKIP_COLS:
            continue
        if is_multi_value(db_name, col):
            where_parts.append("({0} LIKE ?)".format(col))
            params.append("%" + val + "%")
        else:
            where_parts.append("{0} = ?".format(col))
            params.append(val)

    where_clause = ""
    if where_parts:
        where_clause = "WHERE " + " AND ".join(where_parts)

    order_clause = ""
    if order_by:
        safe = order_by.replace(";", "").replace("--", "")
        order_clause = "ORDER BY {0} DESC".format(safe)

    limit_clause = ""
    params_list = list(params)
    if limit:
        limit_clause = "LIMIT ?"
        params_list.append(int(limit))
    if offset:
        limit_clause += " OFFSET ?"
        params_list.append(int(offset))

    sql = "SELECT * FROM {0} {1} {2} {3}".format(db_name, where_clause, order_clause, limit_clause)
    rows = conn.execute(sql, params_list).fetchall()
    conn.close()
    return output_json(rows, db_name)
