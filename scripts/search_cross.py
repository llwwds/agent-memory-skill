# C: Cross-layer search — search events.overview, then find conversations
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_utils import get_conn, deserialize_multi
from db_query_core import query_rows

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Cross-layer: keyword -> events -> conversations")
    p.add_argument("--q", required=True, help="Keyword to search in events.overview")
    p.add_argument("--limit", type=int, default=50)
    a = p.parse_args()

    # Step 1: search events.overview
    conn = get_conn("events")
    like = "%" + a.q + "%"
    event_rows = conn.execute(
        "SELECT name, overview FROM events WHERE overview LIKE ? LIMIT 20",
        (like,)
    ).fetchall()
    conn.close()

    event_names = [r["name"] for r in event_rows]
    print(json.dumps({"step1_matched_events": event_names}, ensure_ascii=False), file=sys.stderr)

    if not event_names:
        print("[]")
        sys.exit(0)

    # Step 2: search conversations by event names (OR logic via multiple LIKEs)
    conn = get_conn("conversations")
    or_parts = " OR ".join(["event LIKE ?"] * len(event_names))
    like_params = ["%" + n + "%" for n in event_names]
    sql = "SELECT * FROM conversations WHERE ({0}) ORDER BY created_at DESC LIMIT ?".format(or_parts)
    rows = conn.execute(sql, like_params + [a.limit]).fetchall()
    conn.close()

    result = []
    for row in rows:
        d = dict(row)
        d["event"] = deserialize_multi(d.get("event",""))
        result.append(d)
    print(json.dumps(result, ensure_ascii=False, indent=2))
