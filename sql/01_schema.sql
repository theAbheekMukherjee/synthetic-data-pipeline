-- ============================================================
--  Synthetic Data Pipeline — Schema DDL
--  Author: Abheek Mukherjee
--  Compatible: PostgreSQL / MySQL / SQLite
-- ============================================================

-- 1. CATEGORIES
CREATE TABLE IF NOT EXISTS categories (
    category_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    description   TEXT
);

-- 2. SUPPLIERS
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id    SERIAL PRIMARY KEY,
    name           VARCHAR(150) NOT NULL,
    country        VARCHAR(80),
    rating         NUMERIC(3,1) CHECK (rating BETWEEN 1 AND 5),
    lead_time_days INT
);

-- 3. PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    product_id   SERIAL PRIMARY KEY,
    name         VARCHAR(200) NOT NULL,
    sku          VARCHAR(50)  UNIQUE NOT NULL,
    category_id  INT REFERENCES categories(category_id),
    supplier_id  INT REFERENCES suppliers(supplier_id),
    unit_cost    NUMERIC(10,2) NOT NULL,
    unit_price   NUMERIC(10,2) NOT NULL,
    stock_qty    INT DEFAULT 0,
    is_active    SMALLINT DEFAULT 1
);

-- 4. PRODUCT_SUPPLIER  (Many-to-Many bridge)
CREATE TABLE IF NOT EXISTS product_supplier (
    product_id     INT REFERENCES products(product_id),
    supplier_id    INT REFERENCES suppliers(supplier_id),
    is_primary     SMALLINT DEFAULT 0,
    unit_cost      NUMERIC(10,2),
    lead_time_days INT,
    PRIMARY KEY (product_id, supplier_id)
);

-- 5. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(80)  NOT NULL,
    last_name     VARCHAR(80)  NOT NULL,
    email         VARCHAR(200) UNIQUE NOT NULL,
    region        VARCHAR(50),
    channel       VARCHAR(50),
    registered_at DATE,
    loyalty_tier  VARCHAR(20) CHECK (loyalty_tier IN ('Bronze','Silver','Gold','Platinum'))
);

-- 6. EMPLOYEES
CREATE TABLE IF NOT EXISTS employees (
    employee_id  SERIAL PRIMARY KEY,
    name         VARCHAR(150) NOT NULL,
    role         VARCHAR(80),
    region       VARCHAR(50),
    hire_date    DATE
);

-- 7. ORDERS
CREATE TABLE IF NOT EXISTS orders (
    order_id       SERIAL PRIMARY KEY,
    customer_id    INT REFERENCES customers(customer_id),
    employee_id    INT REFERENCES employees(employee_id),
    order_date     DATE NOT NULL,
    shipped_date   DATE,
    status         VARCHAR(30) CHECK (status IN (
                       'Pending','Processing','Shipped','Delivered','Cancelled','Returned')),
    payment_type   VARCHAR(50),
    discount_pct   NUMERIC(5,2) DEFAULT 0,
    shipping_cost  NUMERIC(8,2) DEFAULT 0,
    channel        VARCHAR(50)
);

-- 8. ORDER_ITEMS  (Many-to-Many: Orders x Products)
CREATE TABLE IF NOT EXISTS order_items (
    item_id       SERIAL PRIMARY KEY,
    order_id      INT REFERENCES orders(order_id),
    product_id    INT REFERENCES products(product_id),
    quantity      INT NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2) NOT NULL,
    discount_pct  NUMERIC(5,2)  DEFAULT 0,
    line_total    NUMERIC(12,2),
    line_cost     NUMERIC(12,2)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date       ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status);
CREATE INDEX IF NOT EXISTS idx_items_order       ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_items_product     ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
