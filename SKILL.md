---
name: agent-memory-skill
description: >-
  管理分层长期记忆（conversations/events/persona/tools），使用 SQLite 存储，
  基于多值标签进行精确索引和交叉搜索。当 agent 需要读写记忆、查询历史对话、
  维护工具链信息、更新用户画像时使用。提供 A-F 六种检索策略的独立脚本。
metadata:
  short-description: "SQLite 分层记忆系统，多值标签索引，六种检索策略"
---

# Agent Memory Skill

管理 4 个 SQLite 数据库，提供记忆的读写和六种检索策略。

## 数据库路径

```
C:\llwwds_file\memory\
├── conversations.db   原始对话记录
├── events.db          事件（每个事件标签一条记录）
├── persona.db         用户画像（身份/偏好/目标/项目）
└── tools.db           工具链（设备/部署方式/手册）
```

## 核心规则

### 不支持物理删除
任何删除操作仅将 status 改为 不存在，原始数据永久保留。

### 标签多值规则
除 status 和时间戳外，所有标签列支持多值（JSON 数组）：
- device: ["win10pc", "macbook"]
- event: ["agent_sql_memory", "工具链搭建"]

### 增删改查前先查标签池
每个 db 有 _tag_pool 表维护可用标签值。操作前先用 --list-tags 查看。

***

## 检索策略（A-F，6 个独立脚本）

鼓励在一次搜索中综合使用多个方案。

### A — 事件标签过滤
```bash
python scripts/search_event.py --event <事件名> [--db conversations] [--limit 50]
```

### B — 内容关键词搜索
```bash
python scripts/search_content.py --q <关键词> [--db conversations] [--limit 50]
```

### C — 跨层搜索（事件→对话）
```bash
python scripts/search_cross.py --q <关键词> [--limit 50]
```

### D — 事件+内容联合搜索
```bash
python scripts/search_hybrid.py --event <事件名> --q <关键词> [--limit 50]
```

### E — 多标签交叉搜索
```bash
python scripts/search_tags.py --db <db名> [--event X] [--device Y] [--status Z] [--q 词] [--limit 50]
```

### F — 反向关联检索
```bash
python scripts/search_related.py --id <对话id> [--limit 30]
```

***

## 综合搜索策略

| 用户意图 | 推荐方案 |
|----------|----------|
| 查某个项目的所有对话 | A（事件过滤） |
| 不记得属于哪个项目 | C（跨层）→ D（精确命中） |
| 搜项目内的特定话题 | D（事件+内容联合） |
| 精准交叉过滤 | E（多标签） |
| 找关联对话 | F（反向检索） |
| 探索性搜索 | B（内容搜索） |

## 写入操作

```bash
# 插入
python scripts/db_write.py --db tools --action insert --data JSON
# 精确更新
python scripts/db_write.py --db tools --action update --id 3 --set JSON
# 软删除
python scripts/db_write.py --db tools --action delete --id 3
```

## 其他操作

```bash
python scripts/db_query.py --db tools --list-tags --column device
python scripts/db_init.py
python scripts/db_migrate.py --target persona [--dry-run]
```

## 工作流

### 对话开始时
1. 查询标签池：python scripts/db_query.py --db events --list-tags --column name
2. 拉取画像：python scripts/db_query.py --db persona --limit 50
3. 按需拉上下文：根据场景选择 A-F 搜索

### 对话结束时
1. 写 L0：python scripts/db_write.py --db conversations --action insert --data JSON
2. 更新事件：更新 events 的 overview/milestones
3. 工具链变更：更新 tools 表 status
