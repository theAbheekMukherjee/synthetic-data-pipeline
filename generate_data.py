"""
Synthetic Data Pipeline — ETL Generator
Generates 700+ order lifecycles across a relational schema
Author: Abheek Mukherjee
"""

import random
import string
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── CONFIGURATION ────────────────────────────────────────────────────────────
N_CUSTOMERS    = 200
N_PRODUCTS     = 80
N_SUPPLIERS    = 15
N_CATEGORIES   = 8
N_ORDERS       = 750
N_ORDER_ITEMS  = 2200
N_EMPLOYEES    = 30
REGIONS        = ["North", "South", "East", "West", "Central"]
STATUSES       = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled", "Returned"]
PAYMENT_TYPES  = ["Credit Card", "PayPal", "Bank Transfer", "Debit Card"]
CHANNELS       = ["Online", "In-Store", "Phone", "Partner"]

def rand_date(start="2022-01-01", end="2024-12-31"):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end,   "%Y-%m-%d")
    return s + timedelta(days=random.randint(0, (e - s).days))

def rand_str(n=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

# ── CATEGORIES ───────────────────────────────────────────────────────────────
CATEGORY_NAMES = [
    "Electronics", "Apparel", "Home & Garden", "Sports",
    "Books", "Toys", "Beauty", "Automotive"
]
categories = [{"category_id": i+1, "name": CATEGORY_NAMES[i],
               "description": f"{CATEGORY_NAMES[i]} products"}
              for i in range(N_CATEGORIES)]

# ── SUPPLIERS ────────────────────────────────────────────────────────────────
suppliers = [{"supplier_id": i+1,
              "name": f"Supplier_{rand_str(5)}",
              "country": random.choice(["UK", "USA", "Germany", "China", "India"]),
              "rating": round(random.uniform(3.0, 5.0), 1),
              "lead_time_days": random.randint(2, 30)}
             for i in range(N_SUPPLIERS)]

# ── PRODUCTS ─────────────────────────────────────────────────────────────────
PRODUCT_NAMES = [f"Product_{rand_str(6)}" for _ in range(N_PRODUCTS)]
products = []
for i in range(N_PRODUCTS):
    cost  = round(random.uniform(5, 500), 2)
    price = round(cost * random.uniform(1.2, 2.5), 2)
    products.append({
        "product_id":   i+1,
        "name":         PRODUCT_NAMES[i],
        "sku":          rand_str(10),
        "category_id":  random.randint(1, N_CATEGORIES),
        "supplier_id":  random.randint(1, N_SUPPLIERS),
        "unit_cost":    cost,
        "unit_price":   price,
        "stock_qty":    random.randint(0, 500),
        "is_active":    random.choice([1, 1, 1, 0]),
    })

# ── CUSTOMERS ────────────────────────────────────────────────────────────────
FIRST = ["James","Emma","Oliver","Sophia","Noah","Ava","Liam","Isabella","William","Mia"]
LAST  = ["Smith","Jones","Williams","Taylor","Brown","Davies","Evans","Wilson","Thomas","Roberts"]
customers = []
for i in range(N_CUSTOMERS):
    reg_date = rand_date("2020-01-01", "2023-12-31")
    customers.append({
        "customer_id":  i+1,
        "first_name":   random.choice(FIRST),
        "last_name":    random.choice(LAST),
        "email":        f"user{i+1}@example.com",
        "region":       random.choice(REGIONS),
        "channel":      random.choice(CHANNELS),
        "registered_at": reg_date.strftime("%Y-%m-%d"),
        "loyalty_tier": random.choice(["Bronze","Silver","Gold","Platinum"]),
    })

# ── EMPLOYEES ────────────────────────────────────────────────────────────────
ROLES = ["Sales Rep","Account Manager","Logistics","Support","Manager"]
employees = [{"employee_id": i+1,
              "name": f"{random.choice(FIRST)} {random.choice(LAST)}",
              "role": random.choice(ROLES),
              "region": random.choice(REGIONS),
              "hire_date": rand_date("2018-01-01","2023-06-01").strftime("%Y-%m-%d")}
             for i in range(N_EMPLOYEES)]

# ── ORDERS ───────────────────────────────────────────────────────────────────
orders = []
for i in range(N_ORDERS):
    order_date     = rand_date("2022-01-01", "2024-12-31")
    promised_days  = random.randint(3, 14)
    shipped_days   = promised_days + random.randint(-2, 5)
    status         = random.choices(STATUSES, weights=[5,10,15,55,8,7])[0]
    shipped_at     = (order_date + timedelta(days=max(1,shipped_days))).strftime("%Y-%m-%d") \
                     if status not in ["Pending","Processing"] else None
    orders.append({
        "order_id":        i+1,
        "customer_id":     random.randint(1, N_CUSTOMERS),
        "employee_id":     random.randint(1, N_EMPLOYEES),
        "order_date":      order_date.strftime("%Y-%m-%d"),
        "shipped_date":    shipped_at,
        "status":          status,
        "payment_type":    random.choice(PAYMENT_TYPES),
        "discount_pct":    random.choice([0,0,0,5,10,15,20]),
        "shipping_cost":   round(random.uniform(0, 25), 2),
        "channel":         random.choice(CHANNELS),
    })

# ── ORDER ITEMS (Many-to-Many: Orders x Products) ────────────────────────────
order_items = []
item_id = 1
for order in orders:
    n_items = random.choices([1,2,3,4,5], weights=[15,35,30,15,5])[0]
    chosen_products = random.sample(range(1, N_PRODUCTS+1), min(n_items, N_PRODUCTS))
    for prod_id in chosen_products:
        prod  = products[prod_id-1]
        qty   = random.randint(1, 10)
        disc  = random.choice([0,0,0,5,10])
        price = round(prod["unit_price"] * (1 - disc/100), 2)
        order_items.append({
            "item_id":      item_id,
            "order_id":     order["order_id"],
            "product_id":   prod_id,
            "quantity":     qty,
            "unit_price":   price,
            "discount_pct": disc,
            "line_total":   round(price * qty, 2),
            "line_cost":    round(prod["unit_cost"] * qty, 2),
        })
        item_id += 1

# ── PRODUCT_SUPPLIER (Many-to-Many bridge) ───────────────────────────────────
prod_supplier = []
seen = set()
for p in products:
    extra_suppliers = random.sample(range(1, N_SUPPLIERS+1), random.randint(1, 3))
    for s_id in extra_suppliers:
        key = (p["product_id"], s_id)
        if key not in seen:
            seen.add(key)
            prod_supplier.append({
                "product_id":    p["product_id"],
                "supplier_id":   s_id,
                "is_primary":    1 if s_id == p["supplier_id"] else 0,
                "unit_cost":     round(p["unit_cost"] * random.uniform(0.9, 1.1), 2),
                "lead_time_days": random.randint(2, 30),
            })

# ── WRITE CSVs ───────────────────────────────────────────────────────────────
def write_csv(name, rows):
    if not rows:
        return
    fp = OUTPUT_DIR / f"{name}.csv"
    with open(fp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  Written: {fp}  ({len(rows)} rows)")

print("Generating synthetic data...")
write_csv("categories",      categories)
write_csv("suppliers",       suppliers)
write_csv("products",        products)
write_csv("customers",       customers)
write_csv("employees",       employees)
write_csv("orders",          orders)
write_csv("order_items",     order_items)
write_csv("product_supplier", prod_supplier)
print(f"Done. Total order items: {len(order_items)}")
