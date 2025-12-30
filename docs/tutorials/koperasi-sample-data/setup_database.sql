-- Setup script for Koperasi sample database
-- Run this to create the database and load sample data

-- Create database (run as postgres superuser)
-- CREATE DATABASE koperasi_demo;
-- \c koperasi_demo;

-- Create schema
CREATE SCHEMA IF NOT EXISTS public;

-- Create dimension table for geography
CREATE TABLE IF NOT EXISTS dim_geography (
    id INTEGER PRIMARY KEY,
    province_name VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    island_group VARCHAR(50)
);

-- Create dimension table for dates
CREATE TABLE IF NOT EXISTS dim_date (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    day INTEGER,
    week_of_year INTEGER
);

-- Create fact table for KPIs
CREATE TABLE IF NOT EXISTS fact_kpi (
    id INTEGER PRIMARY KEY,
    geography_id INTEGER REFERENCES dim_geography(id),
    date_id INTEGER REFERENCES dim_date(id),
    TotalKoperasiTerdaftar INTEGER,
    TotalAnggota INTEGER,
    TotalAset BIGINT,
    status VARCHAR(20)
);

-- Load data from CSV files
-- Note: Adjust the file paths to match your local system

\COPY dim_geography FROM 'dim_geography.csv' WITH (FORMAT csv, HEADER true);
\COPY dim_date FROM 'dim_date.csv' WITH (FORMAT csv, HEADER true);
\COPY fact_kpi FROM 'fact_kpi.csv' WITH (FORMAT csv, HEADER true);

-- Verify data loaded
SELECT 'dim_geography' as table_name, COUNT(*) as row_count FROM dim_geography
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_kpi', COUNT(*) FROM fact_kpi;

-- Sample queries to test
SELECT
    g.province_name,
    SUM(f.TotalKoperasiTerdaftar) as total_koperasi
FROM fact_kpi f
JOIN dim_geography g ON f.geography_id = g.id
WHERE g.island_group = 'Java'
GROUP BY g.province_name
ORDER BY g.province_name;
