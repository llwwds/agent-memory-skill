# db_migrate.py -- Markdown to SQLite migration
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_utils import DB_FILES, get_conn, now_iso

MD_BASE = r"C:\llwwds_file\obsidian_file\memory"

def migrate_persona(dry_run=False):
    path = os.path.join(MD_BASE, "L3_persona", "persona.md")
    if not os.path.exists(path):
        print("ERROR: persona.md not found at " + path)
        return
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    rows = []
    section = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.startswith("### "):
            section = line[4:].strip()
        elif line.startswith("- **"):
            m = re.match(r"- \*\*(.+?)\*\*[：:]\s*(.*)", line)
            if m and section:
                key = m.group(1).strip()
                content = m.group(2).strip()
                if key and content:
                    rows.append((section, key, content))

    total = len(rows)
    print("Found {0} persona entries".format(total))
    if dry_run:
        for s, k, c in rows[:10]:
            c_short = c[:80] + "..." if len(c) > 80 else c
            print("  [{0}] {1}: {2}".format(s, k, c_short))
        if total > 10:
            print("  ... and {0} more".format(total - 10))
        return

    conn = get_conn("persona")
    now = now_iso()
    count = 0
    for s, k, c in rows:
        try:
            conn.execute(
                "INSERT OR REPLACE INTO persona (section, key, content, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (s, k, c, "存在", now, now),
            )
            count += 1
        except Exception as e:
            print("  SKIP [{0}] {1}: {2}".format(s, k, e))
    conn.commit()
    conn.close()
    print("Imported {0} persona entries".format(count))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Markdown to SQLite migration")
    p.add_argument("--target", choices=["persona", "tools"], default="persona")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    if a.target == "persona":
        migrate_persona(dry_run=a.dry_run)
    else:
        print("Migration for {0} not yet implemented".format(a.target))
        print("Tools migration requires manual audit first per user request")
