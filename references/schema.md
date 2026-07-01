# SQL Schema Reference

## conversations.db

```sql
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    summary TEXT,
    event TEXT DEFAULT '[]',
    device TEXT,
    status TEXT DEFAULT '存在',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conv_event ON conversations(event);
CREATE INDEX IF NOT EXISTS idx_conv_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conv_created ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conv_device ON conversations(device);
```

## events.db

```sql
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    overview TEXT,
    milestones TEXT DEFAULT '[]',
    parent_event TEXT DEFAULT '[]',
    status TEXT DEFAULT '进行中',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_evt_parent ON events(parent_event);
CREATE INDEX IF NOT EXISTS idx_evt_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_evt_created ON events(created_at);
```

## persona.db

```sql
CREATE TABLE IF NOT EXISTS persona (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT NOT NULL,
    key TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '[]',
    version INTEGER DEFAULT 1,
    status TEXT DEFAULT '存在',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(section, key)
);

CREATE INDEX IF NOT EXISTS idx_per_section ON persona(section);
CREATE INDEX IF NOT EXISTS idx_per_status ON persona(status);
```

## tools.db

```sql
CREATE TABLE IF NOT EXISTS tools (
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
);

CREATE INDEX IF NOT EXISTS idx_tool_name ON tools(name);
CREATE INDEX IF NOT EXISTS idx_tool_device ON tools(device);
CREATE INDEX IF NOT EXISTS idx_tool_deployment ON tools(deployment);
CREATE INDEX IF NOT EXISTS idx_tool_event ON tools(event);
CREATE INDEX IF NOT EXISTS idx_tool_status ON tools(status);
```

## _tag_pool (each db)

```sql
CREATE TABLE IF NOT EXISTS _tag_pool (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_name TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    last_used TEXT,
    UNIQUE(column_name, tag_value)
);
```
