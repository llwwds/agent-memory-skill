# Agent Memory Skill

分层长期记忆系统 — 管理 4 个 SQLite 数据库，基于多值标签进行精确索引和交叉搜索。

适用于 Agent 读写记忆、查询历史对话、维护工具链信息、更新用户画像等场景。

---

## 概述

本系统将记忆分为 4 个层次（L0-L3），分别存储在独立的 SQLite 数据库中，提供**读、写、搜索**完整的记忆生命周期管理。

| 层次 | 数据库 | 用途 |
|------|--------|------|
| L0 | conversations.db | 原始对话记录 |
| L1 | events.db | 事件（每个事件标签一条记录） |
| L2 | persona.db | 用户画像（身份/偏好/目标/项目） |
| L3 | 	ools.db | 工具链（设备/部署方式/手册） |

## 核心规则

### 不支持物理删除
任何删除操作仅将 status 改为 不存在，原始数据永久保留。

### 标签多值规则
除 status 和时间戳外，所有标签列支持多值（JSON 数组）：
- device: ["win10pc", "macbook"]
- event: ["agent_sql_memory", "工具链搭建"]

### 增删改查前先查标签池
每个 db 有 _tag_pool 表维护可用标签值。操作前先用 --list-tags 查看。

## 数据库 Schema

参见 [references/schema.md](references/schema.md)

---

## 检索策略（A-F）

提供 6 个独立脚本：

### A — 事件标签过滤
`ash
python scripts/search_event.py --event <事件名> [--db conversations] [--limit 50]
`

### B — 内容关键词搜索
`ash
python scripts/search_content.py --q <关键词> [--db conversations] [--limit 50]
`

### C — 跨层搜索（事件→对话）
`ash
python scripts/search_cross.py --q <关键词> [--limit 50]
`

### D — 事件+内容联合搜索
`ash
python scripts/search_hybrid.py --event <事件名> --q <关键词> [--limit 50]
`

### E — 多标签交叉搜索
`ash
python scripts/search_tags.py --db <db名> [--event X] [--device Y] [--status Z] [--q 词语] [--limit 50]
`

### F — 反向关联检索
`ash
python scripts/search_related.py --id <对话id> [--limit 30]
`

### 场景推荐

| 用户意图 | 推荐方案 |
|----------|----------|
| 查某个项目的所有对话 | A（事件过滤） |
| 不记得属于哪个项目 | C（跨层）→ D（精确命中） |
| 搜项目内的特定话题 | D（事件+内容联合） |
| 精准交叉过滤 | E（多标签） |
| 找关联对话 | F（反向检索） |
| 探索性搜索 | B（内容搜索） |

---

## 写入操作

`ash
# 插入
python scripts/db_write.py --db tools --action insert --data JSON
# 精确更新
python scripts/db_write.py --db tools --action update --id 3 --set JSON
# 软删除
python scripts/db_write.py --db tools --action delete --id 3
`

## 其他操作

`ash
python scripts/db_query.py --db tools --list-tags --column device
python scripts/db_init.py
python scripts/db_migrate.py --target persona [--dry-run]
`

---

## 项目结构

`
agent-memory-skill/
├── SKILL.md              # Codex 技能入口 — 使用说明
├── README.md             # 本文件
├── scripts/              # 核心脚本
│   ├── db_init.py        # 数据库初始化
│   ├── db_write.py       # 写入工具（insert/update/delete）
│   ├── db_query.py       # 查询工具
│   ├── db_query_core.py  # 查询核心函数
│   ├── db_migrate.py     # 数据库迁移
│   ├── db_utils.py       # 共享工具（连接、序列化、标签池）
│   ├── search_event.py   # 策略 A
│   ├── search_content.py # 策略 B
│   ├── search_cross.py   # 策略 C
│   ├── search_hybrid.py  # 策略 D
│   ├── search_tags.py    # 策略 E
│   └── search_related.py # 策略 F
├── references/
│   └── schema.md         # SQL Schema 完整参考
└── agents/
    └── openai.yaml       # Agent 接口配置
├── docs/                # 项目文档
│   ├── todos.md          # 待办事项和待设计问题
│   └── issues/           # 问题记录
│       └── agent-write.md # Agent 写入问题记录
`

## 数据存储位置

默认数据库路径：C:\llwwds_file\memory\

---

## License

MIT

