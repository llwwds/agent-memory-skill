# db_utils.py — 记忆系统共享工具
import sqlite3
import json
import os
from datetime import datetime, timezone

DB_BASE = r"C:\llwwds_file\memory"

DB_FILES = {
    "conversations": os.path.join(DB_BASE, "conversations.db"),
    "events": os.path.join(DB_BASE, "events.db"),
    "persona": os.path.join(DB_BASE, "persona.db"),
    "tools": os.path.join(DB_BASE, "tools.db"),
}

MULTI_VALUE_COLS = {
    "conversations": ["event"],
    "events": ["parent_event"],
    "persona": ["content"],
    "tools": ["device", "deployment", "event"],
}


def get_conn(db_name):
    if db_name not in DB_FILES:
        avail = list(DB_FILES.keys())
        raise ValueError(f"Unknown db {db_name}. Options: {avail}")
    conn = sqlite3.connect(DB_FILES[db_name])
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def get_db_path(db_name):
    if db_name not in DB_FILES:
        avail = list(DB_FILES.keys())
        raise ValueError(f"Unknown db {db_name}. Options: {avail}")
    return DB_FILES[db_name]


def is_multi_value(db_name, col_name):
    return col_name in MULTI_VALUE_COLS.get(db_name, [])


def serialize_multi(value):
    if value is None:
        return json.dumps([])
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return json.dumps(parsed, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            pass
        return json.dumps([value], ensure_ascii=False)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps([str(value)], ensure_ascii=False)


def deserialize_multi(value):
    if value is None:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return [value] if value else []


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sync_tag_pool(conn, table_name, column_name, value):
    values = []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                values = [str(v) for v in parsed]
            else:
                values = [value]
        except (json.JSONDecodeError, TypeError):
            values = [value]
    else:
        values = [str(value)]
    for v in values:
        if not v or v.strip() == "":
            continue
        conn.execute(
            """INSERT INTO _tag_pool (column_name, tag_value, usage_count, last_used)
               VALUES (?, ?, 1, ?)
               ON CONFLICT(column_name, tag_value) DO UPDATE SET
               usage_count = usage_count + 1,
               last_used = excluded.last_used""",
            (column_name, v, now_iso())
        )


def sync_tag_pool_all_columns(conn, table_name, row_data):
    skip_cols = {"id", "content", "summary", "overview", "milestones",
                 "usage_guide", "tech_manual", "created_at", "updated_at"}
    for col, val in row_data.items():
        if col in skip_cols:
            continue
        sync_tag_pool(conn, table_name, col, val)


def output_json(rows, table_name=""):
    result = []
    for row in rows:
        d = dict(row)
        for col in MULTI_VALUE_COLS.get(table_name, []):
            if col in d:
                d[col] = deserialize_multi(d[col])
        result.append(d)
    return json.dumps(result, ensure_ascii=False, indent=2)