# db_init.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_utils import DB_FILES, get_conn, now_iso

TABLES = {
    "conversations": """CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        summary TEXT,
        event TEXT DEFAULT '[]',
        device TEXT,
        status TEXT DEFAULT '存在',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""",

    "events": """CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        overview TEXT,
        milestones TEXT DEFAULT '[]',
        parent_event TEXT DEFAULT '[]',
        status TEXT DEFAULT '进行中',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""",

    "persona": """CREATE TABLE IF NOT EXISTS persona (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section TEXT NOT NULL,
        key TEXT NOT NULL,
        content TEXT NOT NULL DEFAULT '[]',
        version INTEGER DEFAULT 1,
        status TEXT DEFAULT '存在',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(section, key)
    )""",

    "tools": """CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        device TEXT DEFAULT '[]',
        deployment TEXT DEFAULT '[]',
        event TEXT DEFAULT '[]',
        overview TEXT,
        usage_guide TEXT,
        tech_manual TEXT,
        status TEXT DEFAULT '存在',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""",
}

INDEXES = {
    "conversations": [
        "CREATE INDEX IF NOT EXISTS idx_conv_event ON conversations(event)",
        "CREATE INDEX IF NOT EXISTS idx_conv_status ON conversations(status)",
        "CREATE INDEX IF NOT EXISTS idx_conv_created ON conversations(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_conv_device ON conversations(device)",
    ],
    "events": [
        "CREATE INDEX IF NOT EXISTS idx_evt_parent ON events(parent_event)",
        "CREATE INDEX IF NOT EXISTS idx_evt_status ON events(status)",
        "CREATE INDEX IF NOT EXISTS idx_evt_created ON events(created_at)",
    ],
    "persona": [
        "CREATE INDEX IF NOT EXISTS idx_per_section ON persona(section)",
        "CREATE INDEX IF NOT EXISTS idx_per_status ON persona(status)",
    ],
    "tools": [
        "CREATE INDEX IF NOT EXISTS idx_tool_name ON tools(name)",
        "CREATE INDEX IF NOT EXISTS idx_tool_device ON tools(device)",
        "CREATE INDEX IF NOT EXISTS idx_tool_deployment ON tools(deployment)",
        "CREATE INDEX IF NOT EXISTS idx_tool_event ON tools(event)",
        "CREATE INDEX IF NOT EXISTS idx_tool_status ON tools(status)",
    ],
}

TAG_POOL_SQL = """CREATE TABLE IF NOT EXISTS _tag_pool (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_name TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    last_used TEXT,
    UNIQUE(column_name, tag_value)
)"""

DEFAULT_TAGS = {
    "conversations": {
        "event": ["agent_sql_memory", "工具链搭建", "memory_skill_v1"],
        "device": ["win", "mac"],
        "status": ["存在", "不存在"],
    },
    "events": {
        "parent_event": ["2026比赛"],
        "status": ["进行中", "已完成", "已废弃"],
    },
    "persona": {
        "section": ["身份", "偏好", "目标", "项目"],
        "status": ["存在", "不存在"],
    },
    "tools": {
        "device": ["win10pc", "macbook", "android"],
        "deployment": ["虚拟机", "虚拟环境 venv", "容器 docker", "本地", "WSL"],
        "event": ["agent_sql_memory"],
        "status": ["存在", "不存在"],
    },
}


def create_all():
    import time
    n = time.time()
    for db_name in DB_FILES:
        db_path = DB_FILES[db_name]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = get_conn(db_name)
        conn.execute(TAG_POOL_SQL)
        conn.execute(TABLES[db_name])
        for idx_sql in INDEXES.get(db_name, []):
            conn.execute(idx_sql)
        for col, tags in DEFAULT_TAGS.get(db_name, {}).items():
            for tag in tags:
                conn.execute(
                    "INSERT OR IGNORE INTO _tag_pool (column_name, tag_value, usage_count, last_used) VALUES (?, ?, 0, ?)",
                    (col, tag, now_iso()),
                )
        conn.commit()
        conn.close()
        print(f"  OK  {db_name}: {db_path}")
    print(f"\nDone in {time.time()-n:.2f}s ({len(DB_FILES)} databases)")


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python db_init.py     # create/initialize all 4 databases")
        sys.exit(0)
    create_all()
