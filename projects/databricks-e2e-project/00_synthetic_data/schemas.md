## Table Schemas 
These are sample schemas (not run and tested) to ideate on the attributes present in the tables in the Medallion layers

### Bronze Layer (2)
```sql
CREATE TABLE bronze.orders (
    order_id STRING PRIMARY KEY,
    order_timestamp TIMESTAMP,
    restaurant_id STRING,
    customer_id STRING,
    order_type STRING,  -- dine_in, takeaway, delivery
    items STRING,  -- JSON array as string
    total_amount DECIMAL(10,2),
    payment_method STRING,
    order_status STRING,
    _ingestion_timestamp TIMESTAMP
)
CLUSTER BY (DATE(order_timestamp))


CREATE TABLE bronze.reviews (
    review_id STRING PRIMARY KEY,
    order_id STRING,
    customer_id STRING,
    restaurant_id STRING,
    review_text STRING,
    rating INT,
    review_date TIMESTAMP,
    _cdc_operation STRING,  -- INSERT, UPDATE, DELETE
    _cdc_timestamp TIMESTAMP
)
```


### Silver Layer (6)
```sql
CREATE TABLE silver.fact_orders (
    order_id STRING PRIMARY KEY,
    order_timestamp TIMESTAMP,
    order_date DATE,
    order_hour INT,
    day_of_week STRING,
    is_weekend BOOLEAN,
    restaurant_id STRING,
    customer_id STRING,
    order_type STRING,
    item_count INT,
    total_amount DECIMAL(10,2),
    payment_method STRING,
    order_status STRING,
    _ingestion_timestamp TIMESTAMP
)
CLUSTER BY (order_date)


CREATE TABLE silver.fact_order_items (
    order_id STRING,
    item_id STRING,
    restaurant_id STRING,
    order_timestamp TIMESTAMP,
    order_date DATE,
    item_name STRING,
    category STRING,
    quantity INT,
    unit_price DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    _ingestion_timestamp TIMESTAMP,
    PRIMARY KEY (order_id, item_id)
)
CLUSTER BY (order_date)


CREATE TABLE silver.dim_customers (
    customer_id STRING PRIMARY KEY,
    name STRING,
    email STRING,
    phone STRING,
    city STRING,
    join_date DATE,
    _ingestion_timestamp TIMESTAMP
)


CREATE TABLE silver.dim_restaurants (
    restaurant_id STRING PRIMARY KEY,
    name STRING,
    city STRING,
    country STRING,
    address STRING,
    opening_date DATE,
    phone STRING,
    _ingestion_timestamp TIMESTAMP
)


CREATE TABLE silver.dim_menu_items (
    restaurant_id STRING,
    item_id STRING,
    name STRING,
    category STRING,
    price DECIMAL(10,2),
    ingredients STRING,
    is_vegetarian BOOLEAN,
    spice_level STRING,  -- None, Mild, Medium, Hot
    _ingestion_timestamp TIMESTAMP,
    PRIMARY KEY (restaurant_id, item_id)
)


CREATE TABLE silver.fact_reviews (
    review_id STRING PRIMARY KEY,
    order_id STRING,
    customer_id STRING,
    restaurant_id STRING,
    review_text STRING,
    rating INT,
    review_date TIMESTAMP,
    sentiment STRING,  -- positive, neutral, negative
    review_length INT,
    _ingestion_timestamp TIMESTAMP
)
CLUSTER BY (review_date)
```

### Gold Layer
```sql
CREATE TABLE gold.daily_sales_summary (
    order_date DATE PRIMARY KEY,
    total_orders BIGINT,
    total_revenue DECIMAL(12,2),
    avg_order_value DECIMAL(10,2),
    unique_customers BIGINT,
    unique_restaurants BIGINT,
    dine_in_orders BIGINT,
    takeaway_orders BIGINT,
    delivery_orders BIGINT,
    top_restaurant STRING,
    top_restaurant_revenue DECIMAL(12,2),
    _ingestion_timestamp TIMESTAMP,
    PRIMARY KEY (order_date)
)
CLUSTER BY (order_date)


CREATE TABLE gold.customer_360 (
    customer_id STRING,
    snapshot_date DATE,
    customer_name STRING,
    email STRING,
    city STRING,
    loyalty_tier STRING, --TODO: how to calculate on ongoing basis
    join_date DATE,
    
    -- Order Stats
    total_orders BIGINT,
    lifetime_spend DECIMAL(12,2),
    avg_order_value DECIMAL(10,2),
    last_order_date DATE,
    days_since_last_order INT,
    
    -- Preferences
    favorite_restaurant_name STRING,
    favorite_category STRING,
    favorite_item STRING,
    preferred_order_type STRING,
    
    -- Review Stats
    avg_rating_given DECIMAL(3,2),
    total_reviews BIGINT,
    
    -- Risk Flags
    is_at_risk BOOLEAN,  -- No order in 90+ days
    is_vip BOOLEAN,  -- Platinum tier OR lifetime_spend > 5000
    
    _ingestion_timestamp TIMESTAMP,
    PRIMARY KEY (customer_id, snapshot_date)
)

CREATE TABLE gold.reviews (
    review_id STRING PRIMARY KEY,
    order_id STRING,
    customer_id STRING,
    restaurant_id STRING,
    
    review_text STRING,
    sentiment STRING,  -- positive, neutral, negative
    
    -- AI categorization of negative reviews
    issue_delivery BOOLEAN,
    issue_delivery_text STRING,

    issue_quality BOOLEAN,
    issue_quality_text STRING,

    issue_pricing BOOLEAN,
    issue_pricing_text STRING,

    issue_portion_size BOOLEAN,
    issue_portion_size_text STRING,

    rating INT,
    review_date TIMESTAMP,
    review_length INT,
    _ingestion_timestamp TIMESTAMP
)
CLUSTER BY (review_date)


CREATE TABLE gold.restaurant_review_summary (
    restaurant_id STRING PRIMARY KEY,
    snapshot_date DATE,
    restaurant_name STRING,
    city STRING,
    
    -- Review Stats
    total_reviews BIGINT,
    avg_rating DECIMAL(3,2),
    rating_5_count BIGINT,
    rating_4_count BIGINT,
    rating_3_count BIGINT,
    rating_2_count BIGINT,
    rating_1_count BIGINT,
    
    -- Sentiment (for GenAI use case)
    sentiment_positive_count BIGINT,
    sentiment_neutral_count BIGINT,
    sentiment_negative_count BIGINT,
    avg_sentiment_score DECIMAL(3,2),  -- 0.0 to 1.0
    
    -- Recency
    last_review_date DATE,
    days_since_last_review INT,
    
    _ingestion_timestamp TIMESTAMP,
    PRIMARY KEY (restaurant_id, snapshot_date)
)
```