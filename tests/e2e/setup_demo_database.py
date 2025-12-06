#!/usr/bin/env python
"""
Setup Demo Database for KAI E2E Testing
========================================

This script creates and populates a PostgreSQL database with realistic
e-commerce sales data for demonstrating KAI's analytics capabilities.

Tables created:
- regions: Geographic regions
- categories: Product categories
- customers: Customer information
- products: Product catalog
- sales: Sales transactions
- ab_tests: A/B test results
"""

import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

# Database configuration
DB_USER = os.environ.get("USER", "postgres")
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "kai_demo_sales"

DATABASE_URL = f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def create_schema(engine):
    """Create database schema."""
    schema_sql = """
    -- Drop existing tables
    DROP TABLE IF EXISTS sales CASCADE;
    DROP TABLE IF EXISTS ab_tests CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS customers CASCADE;
    DROP TABLE IF EXISTS categories CASCADE;
    DROP TABLE IF EXISTS regions CASCADE;

    -- Create regions table
    CREATE TABLE regions (
        region_id SERIAL PRIMARY KEY,
        region_name VARCHAR(50) NOT NULL UNIQUE,
        country VARCHAR(50) DEFAULT 'USA',
        timezone VARCHAR(50)
    );

    -- Create categories table
    CREATE TABLE categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT
    );

    -- Create customers table
    CREATE TABLE customers (
        customer_id VARCHAR(20) PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100),
        region_id INTEGER REFERENCES regions(region_id),
        signup_date DATE,
        is_premium BOOLEAN DEFAULT FALSE
    );

    -- Create products table
    CREATE TABLE products (
        product_id SERIAL PRIMARY KEY,
        product_name VARCHAR(200) NOT NULL,
        category_id INTEGER REFERENCES categories(category_id),
        base_price DECIMAL(10, 2) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE
    );

    -- Create sales table
    CREATE TABLE sales (
        sale_id SERIAL PRIMARY KEY,
        sale_date TIMESTAMP NOT NULL,
        customer_id VARCHAR(20) REFERENCES customers(customer_id),
        product_id INTEGER REFERENCES products(product_id),
        region_id INTEGER REFERENCES regions(region_id),
        category_id INTEGER REFERENCES categories(category_id),
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        discount_pct DECIMAL(5, 2) DEFAULT 0
    );

    -- Create AB tests table
    CREATE TABLE ab_tests (
        test_id SERIAL PRIMARY KEY,
        test_name VARCHAR(100),
        test_group VARCHAR(20) NOT NULL,
        user_id VARCHAR(20),
        conversion BOOLEAN,
        revenue DECIMAL(10, 2),
        time_on_page_seconds INTEGER,
        test_date DATE
    );

    -- Create indexes for performance
    CREATE INDEX idx_sales_date ON sales(sale_date);
    CREATE INDEX idx_sales_region ON sales(region_id);
    CREATE INDEX idx_sales_category ON sales(category_id);
    CREATE INDEX idx_sales_customer ON sales(customer_id);
    CREATE INDEX idx_ab_tests_group ON ab_tests(test_group);
    """

    with engine.connect() as conn:
        for statement in schema_sql.split(";"):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()

    print("Schema created successfully")


def populate_reference_data(engine):
    """Populate reference tables."""
    # Regions
    regions = pd.DataFrame({
        "region_name": ["North", "South", "East", "West", "Central"],
        "country": ["USA"] * 5,
        "timezone": ["America/New_York", "America/Chicago", "America/New_York", "America/Los_Angeles", "America/Chicago"],
    })
    regions.to_sql("regions", engine, if_exists="append", index=False)

    # Categories
    categories = pd.DataFrame({
        "category_name": ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"],
        "description": [
            "Electronic devices and accessories",
            "Apparel and fashion items",
            "Home improvement and garden supplies",
            "Sports equipment and apparel",
            "Books and publications",
        ],
    })
    categories.to_sql("categories", engine, if_exists="append", index=False)

    print("Reference data populated")
    return regions, categories


def generate_customers(engine, n_customers=500):
    """Generate customer data."""
    np.random.seed(42)

    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emily", "Chris", "Lisa", "Tom", "Amy"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

    customers = []
    for i in range(n_customers):
        customer_id = f"CUST{i+1000:04d}"
        customers.append({
            "customer_id": customer_id,
            "first_name": np.random.choice(first_names),
            "last_name": np.random.choice(last_names),
            "email": f"{customer_id.lower()}@example.com",
            "region_id": np.random.randint(1, 6),
            "signup_date": datetime.now() - timedelta(days=np.random.randint(30, 730)),
            "is_premium": np.random.random() < 0.2,
        })

    df = pd.DataFrame(customers)
    df.to_sql("customers", engine, if_exists="append", index=False)
    print(f"Generated {n_customers} customers")
    return df


def generate_products(engine):
    """Generate product catalog."""
    np.random.seed(42)

    products_data = [
        # Electronics
        ("Smartphone Pro", 1, 799.99),
        ("Wireless Earbuds", 1, 149.99),
        ("Laptop 15\"", 1, 1299.99),
        ("Tablet 10\"", 1, 449.99),
        ("Smart Watch", 1, 299.99),
        # Clothing
        ("Men's T-Shirt", 2, 29.99),
        ("Women's Dress", 2, 79.99),
        ("Jeans", 2, 59.99),
        ("Running Shoes", 2, 119.99),
        ("Winter Jacket", 2, 149.99),
        # Home & Garden
        ("Garden Tools Set", 3, 89.99),
        ("Bedding Set", 3, 129.99),
        ("Kitchen Appliance", 3, 199.99),
        ("Outdoor Furniture", 3, 349.99),
        ("Decor Item", 3, 49.99),
        # Sports
        ("Yoga Mat", 4, 39.99),
        ("Dumbbells Set", 4, 79.99),
        ("Tennis Racket", 4, 129.99),
        ("Bicycle", 4, 499.99),
        ("Camping Gear", 4, 199.99),
        # Books
        ("Fiction Bestseller", 5, 14.99),
        ("Non-Fiction", 5, 19.99),
        ("Cookbook", 5, 29.99),
        ("Technical Manual", 5, 49.99),
        ("Children's Book", 5, 9.99),
    ]

    products = pd.DataFrame(products_data, columns=["product_name", "category_id", "base_price"])
    products["is_active"] = True
    products.to_sql("products", engine, if_exists="append", index=False)
    print(f"Generated {len(products)} products")
    return products


def generate_sales(engine, n_sales=5000):
    """Generate sales transactions with realistic patterns."""
    np.random.seed(42)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Load reference data
    with engine.connect() as conn:
        customers = pd.read_sql("SELECT customer_id, region_id FROM customers", conn)
        products = pd.read_sql("SELECT product_id, category_id, base_price FROM products", conn)

    # Generate dates with seasonality
    dates = pd.date_range(start=start_date, end=end_date, periods=n_sales)
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    seasonality = 1 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)

    # Region weights (different market sizes)
    region_weights = {1: 0.25, 2: 0.20, 3: 0.18, 4: 0.22, 5: 0.15}

    sales = []
    for i in range(n_sales):
        # Select customer and get their region
        customer = customers.sample(1).iloc[0]
        customer_id = customer["customer_id"]
        region_id = customer["region_id"]

        # Select product
        product = products.sample(1).iloc[0]
        product_id = product["product_id"]
        category_id = product["category_id"]
        base_price = float(product["base_price"])

        # Calculate quantity and price with some variance
        quantity = np.random.randint(1, 5)
        price_variance = np.random.uniform(0.9, 1.1)
        unit_price = base_price * price_variance

        # Apply seasonal effect
        seasonal_multiplier = seasonality[i]
        unit_price *= seasonal_multiplier

        # Occasional discount
        discount_pct = 0
        if np.random.random() < 0.15:
            discount_pct = np.random.choice([5, 10, 15, 20, 25])

        total_amount = quantity * unit_price * (1 - discount_pct / 100)

        # Add occasional anomalies (~2%)
        if np.random.random() < 0.02:
            total_amount *= np.random.choice([3, 4, 5])

        sales.append({
            "sale_date": dates[i],
            "customer_id": customer_id,
            "product_id": product_id,
            "region_id": region_id,
            "category_id": category_id,
            "quantity": quantity,
            "unit_price": round(unit_price, 2),
            "total_amount": round(total_amount, 2),
            "discount_pct": discount_pct,
        })

    df = pd.DataFrame(sales)
    df.to_sql("sales", engine, if_exists="append", index=False)
    print(f"Generated {n_sales} sales transactions")
    return df


def generate_ab_tests(engine, n_records=1000):
    """Generate A/B test data."""
    np.random.seed(42)

    test_date = datetime.now().date() - timedelta(days=30)

    # Control group
    control_records = []
    for i in range(n_records // 2):
        control_records.append({
            "test_name": "checkout_flow_v2",
            "test_group": "control",
            "user_id": f"USER{i+1:04d}",
            "conversion": np.random.random() < 0.12,
            "revenue": round(np.random.gamma(2, 25), 2) if np.random.random() < 0.12 else 0,
            "time_on_page_seconds": int(np.random.normal(45, 15)),
            "test_date": test_date,
        })

    # Treatment group (higher conversion)
    treatment_records = []
    for i in range(n_records // 2):
        treatment_records.append({
            "test_name": "checkout_flow_v2",
            "test_group": "treatment",
            "user_id": f"USER{i+500:04d}",
            "conversion": np.random.random() < 0.15,
            "revenue": round(np.random.gamma(2.2, 26), 2) if np.random.random() < 0.15 else 0,
            "time_on_page_seconds": int(np.random.normal(40, 12)),
            "test_date": test_date,
        })

    df = pd.DataFrame(control_records + treatment_records)
    df.to_sql("ab_tests", engine, if_exists="append", index=False)
    print(f"Generated {n_records} A/B test records")
    return df


def create_views(engine):
    """Create helpful views for analysis."""
    views_sql = """
    -- Daily sales summary
    CREATE OR REPLACE VIEW v_daily_sales AS
    SELECT
        DATE(sale_date) as sale_date,
        COUNT(*) as num_transactions,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value,
        SUM(quantity) as total_units
    FROM sales
    GROUP BY DATE(sale_date)
    ORDER BY sale_date;

    -- Regional performance
    CREATE OR REPLACE VIEW v_regional_performance AS
    SELECT
        r.region_name,
        COUNT(s.sale_id) as num_sales,
        SUM(s.total_amount) as total_revenue,
        AVG(s.total_amount) as avg_order_value,
        COUNT(DISTINCT s.customer_id) as unique_customers
    FROM sales s
    JOIN regions r ON s.region_id = r.region_id
    GROUP BY r.region_name
    ORDER BY total_revenue DESC;

    -- Category performance
    CREATE OR REPLACE VIEW v_category_performance AS
    SELECT
        c.category_name,
        COUNT(s.sale_id) as num_sales,
        SUM(s.total_amount) as total_revenue,
        AVG(s.total_amount) as avg_order_value
    FROM sales s
    JOIN categories c ON s.category_id = c.category_id
    GROUP BY c.category_name
    ORDER BY total_revenue DESC;

    -- Customer segments
    CREATE OR REPLACE VIEW v_customer_segments AS
    SELECT
        cu.customer_id,
        cu.is_premium,
        r.region_name,
        COUNT(s.sale_id) as num_purchases,
        SUM(s.total_amount) as total_spent,
        AVG(s.total_amount) as avg_order_value,
        MAX(s.sale_date) as last_purchase
    FROM customers cu
    LEFT JOIN sales s ON cu.customer_id = s.customer_id
    LEFT JOIN regions r ON cu.region_id = r.region_id
    GROUP BY cu.customer_id, cu.is_premium, r.region_name;
    """

    with engine.connect() as conn:
        for statement in views_sql.split(";"):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()

    print("Views created successfully")


def main():
    """Main setup function."""
    print(f"\nConnecting to: {DATABASE_URL}\n")

    engine = create_engine(DATABASE_URL)

    try:
        # Create schema
        create_schema(engine)

        # Populate data
        populate_reference_data(engine)
        generate_customers(engine, n_customers=500)
        generate_products(engine)
        generate_sales(engine, n_sales=5000)
        generate_ab_tests(engine, n_records=1000)

        # Create views
        create_views(engine)

        # Print summary
        print("\n" + "=" * 50)
        print("DATABASE SETUP COMPLETE")
        print("=" * 50)

        with engine.connect() as conn:
            tables = ["regions", "categories", "customers", "products", "sales", "ab_tests"]
            for table in tables:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  {table}: {count:,} records")

        print(f"\nConnection string: {DATABASE_URL}")
        print("=" * 50)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
