# Tableau Dashboard Guide

## Data Source Setup

1. Run `generate_data.py` to create `data/*.csv`
2. Open Tableau Desktop → **Connect → Text File** → select `data/order_items.csv`
3. Add remaining CSVs as **New Data Sources** and join:
   - `order_items` ↔ `orders`      on `order_id`
   - `orders`      ↔ `customers`   on `customer_id`
   - `orders`      ↔ `employees`   on `employee_id`
   - `order_items` ↔ `products`    on `product_id`
   - `products`    ↔ `categories`  on `category_id`
   - `products`    ↔ `suppliers`   on `supplier_id`

---

## Dashboard 1: Revenue & Profitability

| Sheet | Chart Type | Dimensions | Measures |
|-------|-----------|------------|----------|
| Revenue by Category | Horizontal Bar | Category | SUM(line_total), SUM(profit) |
| Profit Margin % | Bar + reference line | Category | margin_pct |
| Revenue vs Cost Scatter | Scatter | Product Name | line_total, line_cost |
| KPI Cards | Big Number | — | Total Revenue, Profit, Margin % |

**Calculated Fields:**
```
Profit   = SUM([line_total]) - SUM([line_cost])
Margin % = SUM([Profit]) / SUM([line_total])
```

---

## Dashboard 2: Sales Trend & Operations

| Sheet | Chart Type | Dimensions | Measures |
|-------|-----------|------------|----------|
| Monthly Revenue Trend | Dual-axis Line | Month(order_date) | Revenue, 3M Rolling Avg |
| Order Status Funnel | Bar | Status | COUNT(order_id) |
| Regional Heatmap | Filled Bar / Map | Region | Revenue |
| MoM Growth | Line with colour | Month | MoM % Change |

**Calculated Fields:**
```
MoM Revenue = WINDOW_SUM(SUM([line_total]),-1,-1)
MoM Change  = (SUM([line_total]) - [MoM Revenue]) / [MoM Revenue]
```

---

## Dashboard 3: Customer Intelligence

| Sheet | Chart Type | Dimensions | Measures |
|-------|-----------|------------|----------|
| LTV by Loyalty Tier | Box-plot | Loyalty Tier | LTV per customer |
| Channel Analysis | Treemap | Channel | Revenue |
| Top 20 Customers | Ranked Table | Customer Name | LTV, Orders, AOV |

---

## Global Filters (apply to all dashboards)
- **Date Range** — order_date
- **Region** — customers.region  
- **Category** — categories.name
- **Status** — orders.status (exclude Cancelled / Returned by default)
