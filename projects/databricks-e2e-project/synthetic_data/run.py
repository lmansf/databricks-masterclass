if __name__ == "__main__":
    from sql_db import generate_data_for_sql_db
    generate_data_for_sql_db()
    
    from historical_orders import generate_historical_orders
    generate_historical_orders()
    
    from reviews import generate_customer_reviews
    generate_customer_reviews(review_percentage=0.01)
