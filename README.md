# 🏗️ Synthetic Data Pipeline Generation & Analytics

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite-336791?logo=postgresql)
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-E97627?logo=tableau)
![License](https://img.shields.io/badge/License-MIT-green)

> **End-to-end data engineering project**: Designed a relational database schema (ERD), engineered ETL scripts simulating **750+ order lifecycles** across **8 tables** with complex Many-to-Many relationships, wrote advanced SQL analytics (Window Functions, RANK, CTEs), and built Tableau dashboards to surface revenue drivers and profit margins.

---

## 📐 Architecture Overview

```
generate_data.py          load_to_db.py          analytics_runner.py
      │                         │                         │
      ▼                         ▼                         ▼
  data/*.csv    ──────►   data/pipeline.db  ──────►  output_reports/*.csv
  (8 tables)              (SQLite / Postgres)          (Tableau ready)
```

---

## 🗂️ Repository Structure

```
synthetic-data-pipeline/
│
├── generate_data.py          # ETL: generates all synthetic CSVs (750+ orders)
├── load_to_db.py             # Loads CSVs into SQLite (or swap for Postgres)
├── analytics_runner.py       # Runs all SQL analytics, exports to CSV
├── requirements.txt
│
├── sql/
│   ├── 01_schema.sql         # Full DDL — 8 tables, FK constraints, indexes
│   └── 02_analytics_queries.sql  # 8 advanced queries (RANK, Window Fns, CTEs)
│
├── erd/
│   └── ERD.md                # Mermaid ERD (renders on GitHub)
│
├── tableau/
│   └── TABLEAU_GUIDE.md      # Step-by-step Tableau setup + calculated fields
│
└── notebooks/
    └── pipeline_walkthrough.ipynb  # Full walkthrough (coming soon)
```

---

## 🗃️ Data Model

| Table | Rows | Description |
|-------|------|-------------|
| `categories` | 8 | Product category taxonomy |
| `suppliers` | 15 | Vendor master with rating & lead time |
| `products` | 80 | SKU catalogue with cost/price |
| **`product_supplier`** | ~160 | **M:M bridge** — products × suppliers |
| `customers` | 200 | CRM with region, loyalty tier, channel |
| `employees` | 30 | Sales reps with region & role |
| `orders` | 750 | Full lifecycle: Pending → Delivered/Returned |
| **`order_items`** | ~2,200 | **M:M bridge** — orders × products |

### ERD Preview
> See [`erd/ERD.md`](erd/ERD.md) for the full interactive Mermaid diagram.

---

## ⚡ Quickstart

```bash
# 1. Clone
git clone https://github.com/theAbheekMukherjee/synthetic-data-pipeline.git
cd synthetic-data-pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate all synthetic data (CSVs → data/)
python generate_data.py

# 4. Load into SQLite
python load_to_db.py

# 5. Run analytics & export reports
python analytics_runner.py
# → output_reports/*.csv (Tableau-ready)
```

---

## 🔍 SQL Analytics Highlights

| Query | Technique | Business Question |
|-------|-----------|------------------|
| Revenue & Profit by Category | CTE + RANK() | Which categories drive the most gross profit? |
| Monthly Revenue Trend | Window SUM + 3M Rolling AVG | Is revenue growing? What's the seasonal pattern? |
| Top 10 Customers LTV | CTE + NTILE(4) + RANK() | Who are our highest-value customers? |
| Product Rank within Category | DENSE_RANK() PARTITION BY | Best performers per category? |
| Order Lifecycle KPIs | Window % + AVG fulfilment days | How fast do orders ship? Where are delays? |
| Regional MoM Growth | LAG() PARTITION BY region | Which regions are growing fastest? |
| Employee Leaderboard | RANK() + DENSE_RANK() | Who are the top sales reps by region? |
| Supplier Cost Variance | STDDEV + RANK() | Which suppliers are most reliable on cost? |

---

## 📊 Tableau Dashboards

Three dashboards built from `output_reports/*.csv`:

1. **Revenue & Profitability** — Revenue by category bar chart, Margin % reference line, KPI cards
2. **Sales Trend & Operations** — Monthly trend with rolling average, Order status funnel, Regional heatmap
3. **Customer Intelligence** — LTV by loyalty tier, Channel analysis, Top 20 customer ranked table

See [`tableau/TABLEAU_GUIDE.md`](tableau/TABLEAU_GUIDE.md) for full setup instructions and calculated fields.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Generation | Python (pandas, random, csv) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Analytics | SQL — CTEs, Window Functions, RANK, LAG, NTILE |
| Visualisation | Tableau Desktop / Tableau Public |
| Schema Design | ERD — Mermaid (rendered on GitHub) |

---

## 🗺️ Roadmap

- [ ] Airflow DAG for scheduled pipeline runs  
- [ ] dbt models for analytics layer  
- [ ] Tableau Public embed link  
- [ ] Streamlit dashboard as alternative to Tableau  
- [ ] Docker Compose with PostgreSQL  

---

## 👤 Author

**Abheek Mukherjee**  
[LinkedIn](https://www.linkedin.com/in/abheek-mukherjee) · [GitHub](https://github.com/theAbheekMukherjee)

---

*MIT License*
