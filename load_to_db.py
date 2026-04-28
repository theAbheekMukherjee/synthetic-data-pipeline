"""
Synthetic Data Pipeline — SQLite Loader
Loads all generated CSVs into a local SQLite database
for SQL query development and testing.
Author: Abheek Mukherjee
"""

import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH  = Path("data/pipeline.db")


def load_table(conn, name: str):
    csv_path = DATA_DIR / f"{name}.csv"
    if not csv_path.exists():
        print(f"  [SKIP] {csv_path} not found — run generate_data.py first")
        return
    df = pd.read_csv(csv_path)
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"  Loaded: {name:25s}  {len(df):>6,} rows")


def main():
    print("Loading synthetic data into SQLite...")
    conn = sqlite3.connect(DB_PATH)
    for table in [
        "categories", "suppliers", "products",
        "customers", "employees",
        "orders", "order_items", "product_supplier",
    ]:
        load_table(conn, table)
    conn.commit()
    conn.close()
    print(f"\nDatabase ready at: {DB_PATH}")
    print("Open with: sqlite3 data/pipeline.db")


if __name__ == "__main__":
    main()
