CREATE TABLE databrickse2eproj.historical_orders (
    order_id VARCHAR(256) PRIMARY KEY,
    order_timestamp DATETIME2,
    restaurant_id VARCHAR(256),
    customer_id VARCHAR(256),
    order_type VARCHAR(256),  -- dine_in, takeaway, delivery
    items VARCHAR(MAX),  -- JSON array as string
    total_amount DECIMAL,
    payment_method VARCHAR(256),
    order_status VARCHAR(256)
);

CREATE TABLE databrickse2eproj.reviews (
    review_id VARCHAR(256) PRIMARY KEY,
    order_id VARCHAR(256),
    customer_id VARCHAR(256),
    restaurant_id VARCHAR(256),
    review_text VARCHAR(MAX),
    rating INT,
    review_timestamp DATETIME2
);

CREATE TABLE databrickse2eproj.customers (
    customer_id VARCHAR(256) PRIMARY KEY,
    name VARCHAR(256),
    email VARCHAR(256),
    phone VARCHAR(256),
    city VARCHAR(256),
    join_date DATE,
);

CREATE TABLE databrickse2eproj.menu_items (
    restaurant_id VARCHAR(256),
    item_id VARCHAR(256),
    name VARCHAR(256),
    category VARCHAR(256),
    price DECIMAL(10,2),
    ingredients VARCHAR(256),
    is_vegetarian BIT,
    spice_level VARCHAR(256),  -- None, Mild, Medium, Hot
    PRIMARY KEY (restaurant_id, item_id)
);

CREATE TABLE databrickse2eproj.restaurants (
    restaurant_id VARCHAR(256) PRIMARY KEY,
    name VARCHAR(256),
    city VARCHAR(256),
    country VARCHAR(256),
    address VARCHAR(MAX),
    opening_date DATE,
    phone VARCHAR(256)
);

-- 1. ENABLE CHANGE TRACKING ON DB
ALTER DATABASE [db-databrickse2eproj] SET CHANGE_TRACKING = ON (CHANGE_RETENTION = 14 DAYS, AUTO_CLEANUP = ON);

-- 2. ENABLE CHANGE TRACKING ON TABLES
ALTER TABLE databrickse2eproj.customers ENABLE CHANGE_TRACKING;
ALTER TABLE databrickse2eproj.historical_orders ENABLE CHANGE_TRACKING;
ALTER TABLE databrickse2eproj.menu_items ENABLE CHANGE_TRACKING;
ALTER TABLE databrickse2eproj.restaurants ENABLE CHANGE_TRACKING;
ALTER TABLE databrickse2eproj.reviews ENABLE CHANGE_TRACKING;

-- 3. ENABLE CDC on DB
USE [db-databrickse2eproj];
EXEC sys.sp_cdc_enable_db;

-- 4. ENABLE CDC ON TABLES --
EXEC sys.sp_cdc_enable_table
    @source_schema = N'databrickse2eproj',
    @source_name   = N'customers',
    @role_name     = NULL;
GO;

EXEC sys.sp_cdc_enable_table
    @source_schema = N'databrickse2eproj',
    @source_name   = N'menu_items',
    @role_name     = NULL;
GO;

EXEC sys.sp_cdc_enable_table
    @source_schema = N'databrickse2eproj',
    @source_name   = N'restaurants',
    @role_name     = NULL;
GO;

EXEC sys.sp_cdc_enable_table
    @source_schema = N'databrickse2eproj',
    @source_name   = N'reviews',
    @role_name     = NULL;
GO;

-- Now run projects/databricks-e2e-project/sql/utility_script.sql
-- https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/sql-server-utility