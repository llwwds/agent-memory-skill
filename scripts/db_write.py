# db_write.py -- Memory write/update/delete tool
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_utils import (DB_FILES, get_conn, now_iso, serialize_multi,
                       sync_tag_pool_all_columns, is_multi_value)

def insert_row(db_name, data_json):
    conn = get_conn(db_name)
    data = json.loads(data_json)
    data.pop("id", None)
    cols = list(data.keys())
    values = []
    for col in cols:
        val = data[col]
        if is_multi_value(db_name, col):
            val = serialize_multi(val)
        values.append(val)
    placeholders = ", ".join(["?"] * len(cols))
    quoted_cols = ", ".join(cols)
    sql = f"INSERT INTO {db_name} ({quoted_cols}) VALUES ({placeholders})"
    cursor = conn.execute(sql, values)
    row_data = dict(zip(cols, values))
    row_data["id"] = cursor.lastrowid
    sync_tag_pool_all_columns(conn, db_name, row_data)
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    print(json.dumps({"id": row_id, "status": "inserted"}, ensure_ascii=False))

def update_row(db_name, row_id, set_json):
    conn = get_conn(db_name)
    updates = json.loads(set_json)
    set_pairs = []
    values = []
    updated_data = {}
    for col, val in updates.items():
        if col == "id":
            continue
        if is_multi_value(db_name, col):
            val = serialize_multi(val)
        set_pairs.append(f"{col} = ?")
        values.append(val)
        updated_data[col] = val
    now = now_iso()
    set_pairs.append("updated_at = ?")
    values.append(now)
    updated_data["updated_at"] = now
    values.append(row_id)
    SEP = ", "
    sql = f"UPDATE {db_name} SET {SEP.join(set_pairs)} WHERE id = ?"
    conn.execute(sql, values)
    updated_data["id"] = row_id
    sync_tag_pool_all_columns(conn, db_name, updated_data)
    conn.commit()
    conn.close()
    print(json.dumps({"id": row_id, "status": "updated"}, ensure_ascii=False))

def delete_row(db_name, row_id):
    conn = get_conn(db_name)
    now = now_iso()
    NOT_EXIST = "不存在"
    conn.execute(f"UPDATE {db_name} SET status = ?, updated_at = ? WHERE id = ?",
                 (NOT_EXIST, now, row_id))
    conn.commit()
    conn.close()
    print(json.dumps({"id": row_id, "status": "deleted (soft)"}, ensure_ascii=False))

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Memory write tool")
    p.add_argument("--db", required=True, choices=list(DB_FILES.keys()))
    p.add_argument("--action", required=True, choices=["insert","update","delete"])
    p.add_argument("--data", help="JSON data for insert")
    p.add_argument("--id", type=int, help="Row id for update/delete")
    p.add_argument("--set", help="JSON data for update")
    a = p.parse_args()
    if a.action == "insert":
        if not a.data: print("ERROR: --data required", file=sys.stderr); sys.exit(1)
        insert_row(a.db, a.data)
    elif a.action == "update":
        if not a.id or not a.set: print("ERROR: --id and --set required", file=sys.stderr); sys.exit(1)
        update_row(a.db, a.id, a.set)
    elif a.action == "delete":
        if not a.id: print("ERROR: --id required", file=sys.stderr); sys.exit(1)
        delete_row(a.db, a.id)
