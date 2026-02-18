from database.connection import get_connection

ALLOWED_TABLES = ["weather_logs", "file_logs", "reports"]


def insert_record(table: str, data: dict):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    conn = get_connection()
    cursor = conn.cursor()

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))

    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, list(data.values()))

    conn.commit()
    conn.close()

    return {"status": "success", "table": table}


def query_records(table: str, limit: int = 10):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_summary(table: str):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
    count = cursor.fetchone()["count"]

    conn.close()

    return {
        "table": table,
        "total_records": count
    }
