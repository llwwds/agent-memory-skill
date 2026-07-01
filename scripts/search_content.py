# B: 按内容关键词搜索（content/summary/overview）
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_query_core import query_rows

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Search by content keyword (LIKE)")
    p.add_argument("--q", required=True, help="Search keyword")
    p.add_argument("--db", default="conversations", choices=["conversations","events","tools"])
    p.add_argument("--status", help="Filter by status (optional)")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--order-by", default="created_at")
    a = p.parse_args()
    filters = {}
    if a.status:
        filters["status"] = a.status
    print(query_rows(a.db, filters, order_by=a.order_by, limit=a.limit, content_like=a.q))
