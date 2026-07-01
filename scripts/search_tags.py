# E: 多标签交叉搜索（任意列组合 AND）
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_query_core import query_rows

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Multi-tag cross search (AND logic)")
    p.add_argument("--db", required=True, choices=["conversations","events","persona","tools"])
    p.add_argument("--event")
    p.add_argument("--device")
    p.add_argument("--deployment")
    p.add_argument("--status")
    p.add_argument("--name")
    p.add_argument("--section")
    p.add_argument("--key")
    p.add_argument("--q", help="Content keyword search")
    p.add_argument("--order-by", default="created_at")
    p.add_argument("--limit", type=int, default=50)
    a = p.parse_args()
    filters = {}
    for col in ["event","device","deployment","status","name","section","key"]:
        val = getattr(a, col, None)
        if val:
            filters[col] = val
    print(query_rows(a.db, filters, order_by=a.order_by, limit=a.limit, content_like=a.q))
