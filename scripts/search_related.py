# F: Reverse search — given a conversation, find related conversations via shared events
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_utils import get_conn, deserialize_multi

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Reverse: find related conversations by shared events")
    p.add_argument("--id", type=int, required=True, help="Source conversation id")
    p.add_argument("--limit", type=int, default=30)
    a = p.parse_args()

    # Step 1: get the source conversation
    conn = get_conn("conversations")
    src = conn.execute("SELECT * FROM conversations WHERE id = ?", (a.id,)).fetchone()
    if not src:
        print(json.dumps({"error": "conversation {0} not found".format(a.id)}, ensure_ascii=False))
        conn.close()
        sys.exit(1)

    src_events = deserialize_multi(src["event"])
    conn.close()

    if not src_events:
        print(json.dumps({"related": [], "note": "source has no event tags"}, ensure_ascii=False))
        sys.exit(0)

    # Step 2: find other conversations with same events (exclude self)
    conn = get_conn("conversations")
    or_parts = " OR ".join(["event LIKE ?"] * len(src_events))
    like_params = ["%" + e + "%" for e in src_events]
    sql = "SELECT * FROM conversations WHERE ({0}) AND id != ? ORDER BY created_at DESC LIMIT ?".format(or_parts)
    params = like_params + [a.id, a.limit]
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    result = []
    for row in rows:
        d = dict(row)
        events = deserialize_multi(d.get("event",""))
        d["event"] = events
        d["shared_events"] = [e for e in src_events if e in events]
        result.append(d)
    print(json.dumps({"source_id": a.id, "source_events": src_events, "related": result}, ensure_ascii=False, indent=2))
