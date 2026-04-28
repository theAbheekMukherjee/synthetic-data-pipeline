-- ============================================================
--  Synthetic Data Pipeline — Advanced Analytics Queries
--  Author: Abheek Mukherjee
--  Techniques: Window Functions, RANK, CTEs, Aggregations
-- ============================================================

-- Q1: REVENUE & PROFIT BY CATEGORY
WITH category_sales AS (
    SELECT
        c.name                                        AS category,
        SUM(oi.line_total)                            AS gross_revenue,
        SUM(oi.line_cost)                             AS total_cost,
        SUM(oi.line_total) - SUM(oi.line_cost)        AS gross_profit,
        COUNT(DISTINCT o.order_id)                    AS num_orders,
        SUM(oi.quantity)                              AS units_sold
    FROM order_items oi
    JOIN orders      o  ON oi.order_id    = o.order_id
    JOIN products    p  ON oi.product_id  = p.product_id
    JOIN categories  c  ON p.category_id  = c.category_id
    WHERE o.status NOT IN ('Cancelled', 'Returned')
    GROUP BY c.name
)
SELECT
    category,
    ROUND(gross_revenue, 2)                                         AS revenue,
    ROUND(gross_profit,  2)                                         AS profit,
    ROUND(100.0 * gross_profit / NULLIF(gross_revenue, 0), 1)      AS profit_margin_pct,
    num_orders,
    units_sold,
    RANK() OVER (ORDER BY gross_revenue DESC)                       AS revenue_rank
FROM category_sales
ORDER BY revenue DESC;


-- Q2: MONTHLY REVENUE TREND WITH RUNNING TOTAL
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_date)            AS month,
        SUM(oi.line_total)                            AS monthly_revenue,
        SUM(oi.line_total) - SUM(oi.line_cost)        AS monthly_profit,
        COUNT(DISTINCT o.order_id)                    AS orders_count
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('Cancelled', 'Returned')
    GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT
    TO_CHAR(month, 'YYYY-MM')                                       AS year_month,
    ROUND(monthly_revenue, 2)                                       AS revenue,
    ROUND(monthly_profit,  2)                                       AS profit,
    orders_count,
    ROUND(SUM(monthly_revenue) OVER (ORDER BY month
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2)     AS cumulative_revenue,
    ROUND(AVG(monthly_revenue) OVER (ORDER BY month
          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)             AS rolling_3m_avg
FROM monthly
ORDER BY month;


-- Q3: TOP 10 CUSTOMERS BY LIFETIME VALUE
WITH customer_ltv AS (
    SELECT
        cu.customer_id,
        cu.first_name || ' ' || cu.last_name          AS customer_name,
        cu.region,
        cu.loyalty_tier,
        cu.channel,
        COUNT(DISTINCT o.order_id)                    AS total_orders,
        SUM(oi.line_total)                            AS lifetime_value,
        SUM(oi.line_total) / COUNT(DISTINCT o.order_id) AS avg_order_value,
        MIN(o.order_date)                             AS first_order,
        MAX(o.order_date)                             AS last_order
    FROM customers   cu
    JOIN orders      o  ON cu.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id     = oi.order_id
    WHERE o.status NOT IN ('Cancelled', 'Returned')
    GROUP BY cu.customer_id, customer_name, cu.region, cu.loyalty_tier, cu.channel
)
SELECT
    customer_name,
    region,
    loyalty_tier,
    channel,
    total_orders,
    ROUND(lifetime_value,   2)   AS ltv,
    ROUND(avg_order_value,  2)   AS aov,
    first_order,
    last_order,
    RANK() OVER (ORDER BY lifetime_value DESC)   AS ltv_rank,
    NTILE(4) OVER (ORDER BY lifetime_value DESC) AS ltv_quartile
FROM customer_ltv
ORDER BY lifetime_value DESC
LIMIT 10;


-- Q4: PRODUCT PERFORMANCE — RANK WITHIN CATEGORY
WITH product_perf AS (
    SELECT
        p.product_id,
        p.name                                            AS product_name,
        c.name                                            AS category,
        SUM(oi.quantity)                                  AS units_sold,
        SUM(oi.line_total)                                AS revenue,
        SUM(oi.line_total) - SUM(oi.line_cost)            AS profit,
        ROUND(100.0 * (SUM(oi.line_total) - SUM(oi.line_cost))
              / NULLIF(SUM(oi.line_total), 0), 1)         AS margin_pct
    FROM order_items oi
    JOIN products   p ON oi.product_id  = p.product_id
    JOIN categories c ON p.category_id  = c.category_id
    JOIN orders     o ON oi.order_id    = o.order_id
    WHERE o.status NOT IN ('Cancelled', 'Returned')
    GROUP BY p.product_id, p.name, c.name
)
SELECT
    product_name,
    category,
    units_sold,
    ROUND(revenue, 2)    AS revenue,
    ROUND(profit,  2)    AS profit,
    margin_pct,
    RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category,
    DENSE_RANK() OVER (ORDER BY revenue DESC)                 AS overall_rank,
    PERCENT_RANK() OVER (ORDER BY revenue)                    AS revenue_percentile
FROM product_perf
ORDER BY category, rank_in_category;


-- Q5: ORDER LIFECYCLE — FULFILMENT TIME ANALYSIS
SELECT
    status,
    COUNT(*)                                                  AS order_count,
    ROUND(AVG(JULIANDAY(shipped_date) - JULIANDAY(order_date)), 1) AS avg_days_to_ship,
    MIN(JULIANDAY(shipped_date) - JULIANDAY(order_date))      AS min_days,
    MAX(JULIANDAY(shipped_date) - JULIANDAY(order_date))      AS max_days,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)        AS pct_of_total
FROM orders
WHERE shipped_date IS NOT NULL
GROUP BY status
ORDER BY order_count DESC;


-- Q6: REGIONAL SALES WITH LAG COMPARISON (MoM)
WITH regional_monthly AS (
    SELECT
        cu.region,
        STRFTIME('%Y-%m', o.order_date)              AS month,
        SUM(oi.line_total)                            AS revenue
    FROM orders      o
    JOIN order_items oi ON o.order_id     = oi.order_id
    JOIN customers   cu ON o.customer_id  = cu.customer_id
    WHERE o.status NOT IN ('Cancelled', 'Returned')
    GROUP BY cu.region, STRFTIME('%Y-%m', o.order_date)
)
SELECT
    region,
    month,
    ROUND(revenue, 2)                                                            AS revenue,
    ROUND(LAG(revenue) OVER (PARTITION BY region ORDER BY month), 2)             AS prev_month,
    ROUND(revenue - LAG(revenue) OVER (PARTITION BY region ORDER BY month), 2)  AS mom_change
FROM regional_monthly
ORDER BY region, month;


-- Q7: EMPLOYEE SALES LEADERBOARD
SELECT
    e.name                                                   AS employee,
    e.role,
    e.region,
    COUNT(DISTINCT o.order_id)                               AS orders_handled,
    ROUND(SUM(oi.line_total), 2)                             AS total_revenue,
    ROUND(AVG(oi.line_total), 2)                             AS avg_order_value,
    RANK()       OVER (ORDER BY SUM(oi.line_total) DESC)     AS revenue_rank,
    DENSE_RANK() OVER (PARTITION BY e.region
                       ORDER BY SUM(oi.line_total) DESC)     AS rank_in_region
FROM employees   e
JOIN orders      o  ON e.employee_id = o.employee_id
JOIN order_items oi ON o.order_id    = oi.order_id
WHERE o.status NOT IN ('Cancelled', 'Returned')
GROUP BY e.employee_id, e.name, e.role, e.region
ORDER BY total_revenue DESC;


-- Q8: SUPPLIER RELIABILITY — COST VARIANCE
SELECT
    s.name                                             AS supplier,
    s.country,
    s.rating,
    COUNT(DISTINCT ps.product_id)                      AS products_supplied,
    ROUND(AVG(ps.unit_cost), 2)                        AS avg_cost,
    ROUND(AVG(ps.lead_time_days), 1)                   AS avg_lead_days,
    RANK() OVER (ORDER BY s.rating DESC)               AS reliability_rank,
    RANK() OVER (ORDER BY AVG(ps.lead_time_days) ASC)  AS speed_rank
FROM suppliers      s
JOIN product_supplier ps ON s.supplier_id = ps.supplier_id
GROUP BY s.supplier_id, s.name, s.country, s.rating
ORDER BY reliability_rank;
