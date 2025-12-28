## 14 Key Insights for Dashboard

### Sales & Revenue (4)
- Total Revenue - SUM(total_amount) from orders
- Average Order Value (AOV) - AVG(total_amount) from orders
- Revenue Growth Rate - Month-over-month % change
- Revenue by Order Type - Breakdown: dine-in/takeaway/delivery

### Order Metrics (4)
- Total Orders - COUNT(DISTINCT order_id)
- Orders by Day of Week - Identify busiest days (day / order count)
- Peak Order Hours - Top 3 hours by order volume (hour / order count)
- Weekend vs Weekday Orders - Compare is_weekend = TRUE/FALSE

### Menu Performance (3)
- Best-Selling Items - Top 10 by quantity sold from order_items
- Revenue by Category - Starter/Main/Dessert/Beverage breakdown
- Average Items per Order - AVG(item_count)

### Customer Metrics (3)
- Total Active Customers - Unique customers with orders
- Loyalty Tier Distribution - % Bronze/Silver/Gold/Platinum
- Customer Growth Rate: New customers per month (% increase)


## 7 Key Insights for GenAI Dashboard

Filter by restaurant, date range;

* Review Volume over time
* AI powered insights (last X days)
* Sentiment trend (Line chart showing positive/negative trend over time)
* Top (3) praised items 
* Most (3) criticized items 
* Recent Review feed
* AI auto-categorizes negative reviews:
    - Delivery issues (%)
    - Food quality (%)
    - Service (%)
    - Pricing (%)
    - Portion size (%)
