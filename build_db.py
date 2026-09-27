"""
build_db.py -- Load cleaned order data and regions master into a local SQLite database.
"""
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CLEAN_DATA_PATH = BASE_DIR / "orders_clean.csv"
REGIONS_MASTER_PATH = BASE_DIR / "regions_master.csv"
DB_PATH = BASE_DIR / "pharmeasy.db"


def build_database(
        clean_path: Path = CLEAN_DATA_PATH,
        regions_path: Path = REGIONS_MASTER_PATH,
        db_path: Path = DB_PATH,
) -> None:
    orders_df = pd.read_csv(clean_path)
    regions_df = pd.read_csv(regions_path)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    orders_df.to_sql("orders_clean", conn, index=False, if_exists="replace")
    regions_df.to_sql("regions_master", conn, index=False, if_exists="replace")
    conn.close()

    # Verify
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    orders_count = cur.execute("SELECT COUNT(*) FROM orders_clean").fetchone()[0]
    regions_count = cur.execute("SELECT COUNT(*) FROM regions_master").fetchone()[0]
    conn.close()

    print(f"pharmeasy.db built: orders_clean={orders_count} rows, regions_master={regions_count} rows.")


if __name__ == "__main__":
    build_database()