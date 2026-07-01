# Agent 写入问题记录

> agent 通过 db_write.py 将记忆写入 SQLite 时遇到的问题记录

---

## 问题 1：db_write.py 插入数据时需要手动指定 created_at/updated_at

**日期**: 2026-07-01
**场景**: agent 执行 L0 归档
**描述**: 调用 db_write.py --action insert 时，data JSON 必须包含 created_at 和 updated_at 字段，否则会因 NOT NULL 约束报错。agent 需要额外调用 
ow_iso() 生成时间戳。
**建议**: 考虑在 db_write.py 的 insert_row 中自动填充时间戳，或设为 DEFAULT 值。

---

## 问题 2：标签池（_tag_pool）同步可能覆盖已有标签

**日期**: 2026-07-01
**场景**: 多次写入同一事件名
**描述**: sync_tag_pool_all_columns 使用 ON CONFLICT DO UPDATE 递增 usage_count，但如果写入时 event 字段格式不统一（如 [\"win装git\"] vs ['win装git']），可能导致同一事件名被当作不同标签值插入。
**建议**: 序列化时统一格式，或在标签池层面做 normalize。

---

## 问题 3：PowerShell 转义导致 JSON 传递失败

**日期**: 2026-07-01
**场景**: agent 在 Windows PowerShell 中调用 db_write.py --data
**描述**: ARGPARSE 解析时如果 JSON 包含中文或特殊字符，PowerShell 的转义规则会导致解析错误。需改用内联 Python 脚本或临时文件传递数据。
**建议**: 增加一个 --data-file 参数接收 JSON 文件路径，绕过 shell 转义。
