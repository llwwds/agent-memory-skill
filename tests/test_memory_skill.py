import contextlib
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest


SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import db_init
import db_query
import db_utils
import db_write


class MemorySkillSmokeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        for db_name in db_utils.DB_FILES:
            db_utils.DB_FILES[db_name] = os.path.join(
                self.temp_dir.name, f"{db_name}.db"
            )
        with contextlib.redirect_stdout(io.StringIO()):
            db_init.create_all()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_insert_adds_timestamps_and_normalizes_multi_value_tags(self):
        payload = {
            "content": "README published",
            "summary": "publish",
            "event": ["sqlite_memory_skill项目", "工具链"],
            "device": "macbook",
            "status": "存在",
        }
        with contextlib.redirect_stdout(io.StringIO()):
            db_write.insert_row("conversations", json.dumps(payload, ensure_ascii=False))

        conn = sqlite3.connect(db_utils.DB_FILES["conversations"])
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM conversations").fetchone()
        tags = {
            item[0]
            for item in conn.execute(
                "SELECT tag_value FROM _tag_pool WHERE column_name = 'event'"
            ).fetchall()
        }
        conn.close()

        self.assertTrue(row["created_at"])
        self.assertEqual(row["created_at"], row["updated_at"])
        self.assertEqual(
            json.loads(row["event"]),
            ["sqlite_memory_skill项目", "工具链"],
        )
        self.assertIn("sqlite_memory_skill项目", tags)
        self.assertIn("工具链", tags)

    def test_generic_content_search_uses_columns_that_exist_in_each_database(self):
        payload = {
            "name": "sqlite_memory_skill项目",
            "overview": "SQLite memory project",
            "status": "进行中",
        }
        with contextlib.redirect_stdout(io.StringIO()):
            db_write.insert_row("events", json.dumps(payload, ensure_ascii=False))

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            db_query.query_rows("events", {}, "created_at", 50, 0, "SQLite")

        result = json.loads(output.getvalue())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "sqlite_memory_skill项目")

    def test_delete_is_soft_delete(self):
        payload = {
            "section": "偏好",
            "key": "测试",
            "content": ["保留原始数据"],
            "status": "存在",
        }
        insert_output = io.StringIO()
        with contextlib.redirect_stdout(insert_output):
            db_write.insert_row("persona", json.dumps(payload, ensure_ascii=False))
        row_id = json.loads(insert_output.getvalue())["id"]

        with contextlib.redirect_stdout(io.StringIO()):
            db_write.delete_row("persona", row_id)

        conn = sqlite3.connect(db_utils.DB_FILES["persona"])
        row = conn.execute(
            "SELECT status FROM persona WHERE id = ?", (row_id,)
        ).fetchone()
        conn.close()
        self.assertEqual(row[0], "不存在")


if __name__ == "__main__":
    unittest.main()
