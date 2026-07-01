# Backlog

> 下一步开发可优化或新增的内容。每条记录独立追踪。
> 替代旧的 docs/todos.md，内容已迁移至此。

---

- **类型**: BUG / IDEA / DESIGN / QUESTION
- **状态**: Open / In Progress / Done / Won't Do

---

## B-001 | Agent 写入问题

| 字段 | 值 |
|------|-----|
| 类型 | BUG |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | High |

Agent 通过 db_write.py 写入记忆时遇到多个问题：

- db_write.py insert 时需手动传 created_at/updated_at，违反 DRY
- 标签池（_tag_pool）同步时 event 字段格式不统一会导致标签值重复
- PowerShell 转义规则导致 JSON 传参失败，需改用临时文件传递

**详情** → [docs/issues/agent-write.md](issues/agent-write.md)

---

## B-002 | Agent 事件决策逻辑

| 字段 | 值 |
|------|-----|
| 类型 | DESIGN |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | High |

Agent 如何决定什么内容构成一个「新事件」？如何在一段对话中为所有写入内容准确维护多事件标签？

**核心问题**：
- L1（事件）的粒度由谁决定？agent 自行判断还是用户指定？
- 一段操作可能同时属于多个事件（如"安装 git"同时属于"工具链搭建"），如何自动为 L0 打上多事件标签？
- 事件层级（parent_event）如何自动推导？

**思路方向**：
- 参考 AGENTS.md 的对话流程：对话开始读 L3，结束归档 L0 + 提取 L1
- L1 提取时机在对话结束时，此时上下文最完整
- 可能需要设计「事件匹配规则」：根据关键词、项目引用、工具操作等自动判断归属
- 多事件标签 → L0 可关联多个 L1，支持跨事件搜索

---

## B-003 | db_write.py 自动填充时间戳

| 字段 | 值 |
|------|-----|
| 类型 | BUG |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Medium |

insert_row() 要求 data JSON 必须包含 created_at 和 updated_at，否则 NOT NULL 约束报错。

**改进**：在 insert_row 中自动填充时间戳，或在 SQL schema 中设 DEFAULT 值。

---

## B-004 | 标签池去重标准化

| 字段 | 值 |
|------|-----|
| 类型 | BUG |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Medium |

sync_tag_pool_all_columns 使用 ON CONFLICT DO UPDATE 递增 usage_count，但如果 event 字段格式不统一（如 [\"win装git\"] vs ['win装git']），同一事件名会被当不同标签值插入。

**改进**：序列化时统一格式，或在标签池层面做 normalize。

---

## B-005 | PowerShell JSON 转义问题

| 字段 | 值 |
|------|-----|
| 类型 | BUG |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Medium |

PowerShell 中转义规则导致在命令行调用 db_write.py --data 时，含中文或特殊字符的 JSON 解析失败。

**改进**：增加 --data-file 参数接收 JSON 文件路径，绕过 shell 转义。

---

## B-006 | gh CLI 缺少 read:org scope

| 字段 | 值 |
|------|-----|
| 类型 | BUG |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Low |

当前 OAuth token 缺少 ead:org 权限，gh auth login --with-token 无法直接使用，需手动写 hosts.yml。

**影响**：无法操作组织仓库。可通过 gh auth refresh -h github.com --scopes read:org 补充。

---

## B-007 | git/gh PATH 持久化问题

| 字段 | 值 |
|------|-----|
| 类型 | BUG |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Medium |

Git 和 gh 路径已添加到 Machine/User PATH，但新 PowerShell 进程从父进程继承环境变量，不读注册表。需重新登录 Windows 才能对新进程生效。

**影响**：新终端中 git、gh 命令找不到；gh auth setup-git 失败。

**改进**：考虑添加到 PowerShell profile 中自动加载。

---

## B-008 | multi-event 多标签写回

| 字段 | 值 |
|------|-----|
| 类型 | IDEA |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Low |

当前 L0 归档时 event 字段已支持多值（JSON 数组），但 agent 写入时没有标准化流程来判定一个对话属于哪些事件。

**改进**：设计事件匹配规则，在 L0 归档时自动根据上下文打多事件标签。

---

## B-009 | 工具链状态自动同步

| 字段 | 值 |
|------|-----|
| 类型 | IDEA |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Low |

工具的 status、deployment 等字段需要 agent 手动更新。可考虑在事件完成时联动更新关联工具的状态。

**场景**：装gh_cli 事件完成后，自动将 win端gh_cli 工具的 status 从 进行中 变为 存在。

---

## B-010 | 内存系统 CRLF/LF 跨平台兼容

| 字段 | 值 |
|------|-----|
| 类型 | BUG |
| 状态 | Open |
| 创建 | 2026-07-01 |
| 优先级 | Low |

Windows 上 git 操作提示 LF will be replaced by CRLF。该 repo 可能跨平台使用（Win + Mac），需统一换行符策略。

**改进**：添加 .gitattributes：* text=auto 或逐目录指定。