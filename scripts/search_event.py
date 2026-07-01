# A: 按事件标签精确过滤
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_query_core import query_rows

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Search by event tag")
    p.add_argument("--event", required=True, help="Event tag (multi-value matched via LIKE)")
    p.add_argument("--db", default="conversations", choices=["conversations","tools"])
    p.add_argument("--status", help="Filter by status (optional)")
    p.add_argument("--limit", type=int, default=50)
    a = p.parse_args()
    filters = {"event": a.event}
    if a.status:
        filters["status"] = a.status
    print(query_rows(a.db, filters, order_by="created_at", limit=a.limit))
