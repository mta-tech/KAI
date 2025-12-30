# Koperasi Sample Data

Sample dataset for the KAI tutorial on analyzing Indonesian cooperative (koperasi) data.

## Contents

- `dim_geography.csv` - Province dimension (15 provinces)
- `dim_date.csv` - Date dimension (13 sample dates)
- `fact_kpi.csv` - KPI facts (15 records with koperasi statistics)
- `setup_database.sql` - SQL script to create tables and load data

## Database Schema

### dim_geography
Province dimension table containing Indonesian provinces.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| province_name | VARCHAR(100) | Province name |
| region | VARCHAR(100) | Regional subdivision |
| island_group | VARCHAR(50) | Island grouping (Java, Sumatra, etc.) |

### dim_date
Date dimension for time-based analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| date | DATE | Calendar date |
| year | INTEGER | Year |
| quarter | INTEGER | Quarter (1-4) |
| month | INTEGER | Month (1-12) |
| month_name | VARCHAR(20) | Month name |
| day | INTEGER | Day of month |
| week_of_year | INTEGER | Week number |

### fact_kpi
Fact table containing cooperative KPIs.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| geography_id | INTEGER | Foreign key to dim_geography |
| date_id | INTEGER | Foreign key to dim_date |
| TotalKoperasiTerdaftar | INTEGER | Total registered cooperatives |
| TotalAnggota | INTEGER | Total members |
| TotalAset | BIGINT | Total assets (IDR) |
| status | VARCHAR(20) | Status (active/inactive) |

## Quick Setup

### Method 1: Using psql

```bash
# Create database
createdb koperasi_demo

# Navigate to this directory
cd docs/tutorials/koperasi-sample-data

# Run setup script
psql -d koperasi_demo -f setup_database.sql
```

### Method 2: Using Docker PostgreSQL

```bash
# Start PostgreSQL
docker run -d \
  --name postgres_koperasi \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=koperasi_demo \
  -p 5432:5432 \
  postgres:15

# Wait for PostgreSQL to start
sleep 5

# Copy files into container
docker cp dim_geography.csv postgres_koperasi:/tmp/
docker cp dim_date.csv postgres_koperasi:/tmp/
docker cp fact_kpi.csv postgres_koperasi:/tmp/

# Create tables
docker exec -i postgres_koperasi psql -U postgres -d koperasi_demo <<EOF
CREATE TABLE dim_geography (
    id INTEGER PRIMARY KEY,
    province_name VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    island_group VARCHAR(50)
);

CREATE TABLE dim_date (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    day INTEGER,
    week_of_year INTEGER
);

CREATE TABLE fact_kpi (
    id INTEGER PRIMARY KEY,
    geography_id INTEGER REFERENCES dim_geography(id),
    date_id INTEGER REFERENCES dim_date(id),
    TotalKoperasiTerdaftar INTEGER,
    TotalAnggota INTEGER,
    TotalAset BIGINT,
    status VARCHAR(20)
);
EOF

# Load data
docker exec -i postgres_koperasi psql -U postgres -d koperasi_demo <<EOF
\COPY dim_geography FROM '/tmp/dim_geography.csv' WITH (FORMAT csv, HEADER true);
\COPY dim_date FROM '/tmp/dim_date.csv' WITH (FORMAT csv, HEADER true);
\COPY fact_kpi FROM '/tmp/fact_kpi.csv' WITH (FORMAT csv, HEADER true);
EOF

# Verify
docker exec postgres_koperasi psql -U postgres -d koperasi_demo -c "SELECT COUNT(*) FROM fact_kpi;"
```

### Method 3: Manual Import

1. Create the database:
   ```sql
   CREATE DATABASE koperasi_demo;
   ```

2. Run the SQL from `setup_database.sql` to create tables

3. Import CSVs using your preferred tool:
   - pgAdmin
   - DBeaver
   - DataGrip
   - Or any PostgreSQL client

## Connection String

After setup, connect to the database:

```bash
postgresql://postgres:postgres@localhost:5432/koperasi_demo
```

## Data Overview

This sample dataset contains:
- **15 provinces** across Java, Sumatra, Bali, Kalimantan, and Sulawesi
- **13 date records** spanning 2024
- **15 KPI records** with cooperative statistics

**Java provinces** (total: 91 cooperatives):
- DKI Jakarta: 8
- Jawa Barat: 25
- Jawa Tengah: 18
- DI Yogyakarta: 6
- Jawa Timur: 22
- Banten: 12

This data is used in the tutorial to demonstrate KAI's ability to learn domain knowledge through skills and instructions.
