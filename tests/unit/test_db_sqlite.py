from app.infrastructure.db import SQLiteDatabase


def test_sqlite_row_factory(tmp_path):
    db = SQLiteDatabase(str(tmp_path / "x.db"))
    with db.connect() as conn:
        cur = conn.execute("SELECT 1 AS a")
        row = cur.fetchone()
        assert row["a"] == 1
