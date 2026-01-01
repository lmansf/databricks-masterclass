from pyspark import pipelines as dp
import pyspark.sql.functions as F
from pyspark.sql.types import *
from datetime import datetime


@dp.table(
    name="03_gold.d_sales_summary",
    partition_cols=["order_date"],
    spark_conf={"spark.sql.sources.partitionOverwriteMode": "dynamic"},
    comment="Gold layer aggregates with date-based overwrites",
)
def d_sales_summary():
    df_daily_agg = (
        dp.read("02_silver.fact_orders")
        .groupBy("order_date")
        .agg(
            F.countDistinct("order_id").alias("total_orders"),
            F.sum("total_amount").alias("total_revenue"),
            F.avg("total_amount").alias("avg_order_value"),
            F.countDistinct("customer_id").alias("unique_customers"),
            F.countDistinct("restaurant_id").alias("unique_restaurants"),
            F.sum(F.when(F.col("order_type") == "dine_in", 1).otherwise(0)).alias(
                "dine_in_orders"
            ),
            F.sum(F.when(F.col("order_type") == "takeaway", 1).otherwise(0)).alias(
                "takeaway_orders"
            ),
            F.sum(F.when(F.col("order_type") == "delivery", 1).otherwise(0)).alias(
                "delivery_orders"
            ),
        )
        .withColumn("_ingestion_timestamp", F.current_timestamp())
        .select(
            "order_date",
            "total_orders",
            "total_revenue",
            "avg_order_value",
            "unique_customers",
            "unique_restaurants",
            "dine_in_orders",
            "takeaway_orders",
            "delivery_orders",
            "_ingestion_timestamp",
        )
    )
    return df_daily_agg
