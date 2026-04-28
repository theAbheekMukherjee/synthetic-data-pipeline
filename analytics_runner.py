"""
Synthetic Data Pipeline — Analytics Runner
Executes all SQL analytics queries and exports results to CSV.
Author: Abheek Mukherjee
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH  = Path("data/pipeline.db")
OUT_DIR  = Path("output_reports")
OUT_DIR.mkdir(exist_ok=True)

QUERIES = {
    "revenue_by_category": """
        WITH cs AS (
            SELECT c.name AS category,
                   SUM(oi.line_total)             AS revenue,
                   SUM(oi.line_cost)              AS cost,
                   SUM(oi.line_total)-SUM(oi.line_cost) AS profit,
                   COUNT(DISTINCT o.order_id)     AS num_orders,
                   SUM(oi.quantity)               AS units_sold
            FROM order_items oi
            JOIN orders     o  ON oi.order_id   = o.order_id
            JOIN products   p  ON oi.product_id = p.product_id
            JOIN categories c  ON p.category_id = c.category_id
            WHERE o.status NOT IN ('Cancelled','Returned')
            GROUP BY c.name
        )
        SELECT category,
               ROUND(revenue,2)  AS revenue,
               ROUND(profit,2)   AS profit,
               ROUND(100.0*profit/MAX(revenue,1),1) AS margin_pct,
               num_orders, units_sold
        FROM cs ORDER BY revenue DESC
    """,
    "monthly_revenue_trend": """
        SELECT STRFTIME('%Y-%m', o.order_date)    AS year_month,
               ROUND(SUM(oi.line_total),2)        AS revenue,
               ROUND(SUM(oi.line_total)-SUM(oi.line_cost),2) AS profit,
               COUNT(DISTINCT o.order_id)         AS orders_count
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status NOT IN ('Cancelled','Returned')
        GROUP BY STRFTIME('%Y-%m', o.order_date)
        ORDER BY year_month
    """,
    "top_customers_ltv": """
        SELECT cu.first_name||' '||cu.last_name   AS customer,
               cu.region, cu.loyalty_tier, cu.channel,
               COUNT(DISTINCT o.order_id)         AS orders,
               ROUND(SUM(oi.line_total),2)        AS ltv,
               ROUND(SUM(oi.line_total)/MAX(COUNT(DISTINCT o.order_id),1),2) AS aov
        FROM customers cu
        JOIN orders      o  ON cu.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id     = oi.order_id
        WHERE o.status NOT IN ('Cancelled','Returned')
        GROUP BY cu.customer_id
        ORDER BY ltv DESC
        LIMIT 20
    """,
    "product_performance": """
        SELECT p.name AS product, c.name AS category,
               SUM(oi.quantity)           AS units_sold,
               ROUND(SUM(oi.line_total),2)         AS revenue,
               ROUND(SUM(oi.line_total)-SUM(oi.line_cost),2) AS profit,
               ROUND(100.0*(SUM(oi.line_total)-SUM(oi.line_cost))/MAX(SUM(oi.line_total),1),1) AS margin_pct
        FROM order_items oi
        JOIN products   p ON oi.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN orders     o ON oi.order_id   = o.order_id
        WHERE o.status NOT IN ('Cancelled','Returned')
        GROUP BY p.product_id
        ORDER BY revenue DESC
    """,
    "regional_sales": """
        SELECT cu.region,
               STRFTIME('%Y-%m', o.order_date)   AS year_month,
               COUNT(DISTINCT o.order_id)        AS orders,
               ROUND(SUM(oi.line_total),2)       AS revenue
        FROM orders o
        JOIN order_items oi ON o.order_id    = oi.order_id
        JOIN customers   cu ON o.customer_id = cu.customer_id
        WHERE o.status NOT IN ('Cancelled','Returned')
        GROUP BY cu.region, STRFTIME('%Y-%m', o.order_date)
        ORDER BY cu.region, year_month
    """,
    "order_status_summary": """
        SELECT status,
               COUNT(*)                    AS count,
               ROUND(SUM(oi.line_total),2) AS revenue,
               ROUND(AVG(oi.line_total),2) AS avg_order_value
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY status
        ORDER BY count DESC
    "",
}


def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run load_to_db.py first.")
        return
    conn = sqlite3.connect(DB_PATH)
    print("Running analytics queries...")
    for name, query in QUERIES.items():
        try:
            df = pd.read_sql_query(query, conn)
            out = OUT_DIR / f"{name}.csv"
            df.to_csv(out, index=False)
            print(f"  {name:35s} -> {len(df):>4} rows  [{out}]")
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
    conn.close()
    print("\nAll reports exported to output_reports/")


if __name__ == "__main__":
    main()
