import pandas as pd
import random
import requests
import os
import time
from datetime import datetime, timedelta
import json

# ============================================
# API CONFIGURATION
# ============================================
from dotenv import load_dotenv
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# ============================================
# FOLDERS
# ============================================
script_dir = os.path.dirname(os.path.abspath(__file__))
POSITIVE_FOLDER = os.path.join(script_dir, "data", "feedback_images", "positive")
NEGATIVE_FOLDER = os.path.join(script_dir, "data", "feedback_images", "negative")

os.makedirs(POSITIVE_FOLDER, exist_ok=True)
os.makedirs(NEGATIVE_FOLDER, exist_ok=True)

# ============================================
# LOAD HISTORICAL ORDERS
# ============================================
df_orders = pd.read_csv(os.path.join(script_dir, "data", "historical_orders.csv"))

# ============================================
# REVIEW TEMPLATES
# ============================================
REVIEW_TEMPLATES = {
    5: [
        "Absolutely amazing {dishes}! The {highlight} was cooked to perfection. Fresh ingredients and authentic flavors. Highly recommend!",
        "Outstanding experience! The {dishes} exceeded all expectations. {highlight} was the star of the meal. Will definitely order again!",
        "Best Indian food in UAE! {dishes} were incredible. {highlight} had the perfect balance of spices. Five stars!",
        "Exceptional quality! Ordered {dishes} and everything was delicious. The {highlight} melted in my mouth. Perfect!",
        "Wow! Just wow! {dishes} were all fantastic. {highlight} was particularly memorable. Can't wait to order again!",
        "Hands down the best {highlight} I've ever had! {dishes} were all prepared beautifully. Fresh and flavorful!",
        "Incredible meal! {dishes} arrived hot and fresh. The {highlight} was absolutely divine. Highly satisfied!",
        "Perfect in every way! {dishes} were all excellent. {highlight} stood out with its rich, authentic taste.",
    ],
    4: [
        "Really good {dishes}! The {highlight} was delicious. Slight delay in delivery but food quality made up for it.",
        "Great food overall. {dishes} were tasty, especially the {highlight}. Would order again!",
        "Enjoyed the {dishes}! {highlight} was very good. Portion sizes were generous. Recommend!",
        "Solid experience. {dishes} were well-prepared. {highlight} had great flavor. Minor issues with packaging.",
        "Very satisfied! {dishes} were fresh and flavorful. {highlight} was the standout dish.",
        "Good quality food. {dishes} were nicely done. {highlight} could have been slightly spicier but still good!",
        "Pleasant meal! {dishes} arrived warm. {highlight} was tasty though not exceptional. Would order again.",
    ],
    3: [
        "Decent food but nothing special. {dishes} were okay. {highlight} lacked the punch I expected.",
        "Average experience. {dishes} were fine but {highlight} was a bit bland. Room for improvement.",
        "Mixed feelings. {dishes} were acceptable. {highlight} was decent but portion was small for the price.",
        "It was okay. {dishes} arrived lukewarm. {highlight} tasted fine but could be better.",
        "Not bad, not great. {dishes} were edible. {highlight} needed more seasoning.",
        "Mediocre. {dishes} were fine but forgettable. {highlight} didn't stand out.",
    ],
    2: [
        "Disappointed with {dishes}. {highlight} was cold when it arrived. Not worth the money.",
        "Below expectations. {dishes} were underwhelming. {highlight} was overcooked and dry.",
        "Not good. {dishes} arrived late and cold. {highlight} had barely any flavor. Poor quality.",
        "Unsatisfactory. {dishes} were not fresh. {highlight} tasted reheated. Won't order again.",
        "Poor experience. {dishes} were disappointing. {highlight} was burnt on the edges. Very unhappy.",
        "Expected better. {dishes} were subpar. {highlight} was too oily and greasy. Stomach upset followed.",
    ],
    1: [
        "Terrible experience! {dishes} were all inedible. {highlight} was completely burnt. Waste of money!",
        "Absolutely horrible! {dishes} arrived ice cold after 2 hour delay. {highlight} was spoiled. Disgusting!",
        "Worst food ever! {dishes} were all wrong. {highlight} made me sick. Never ordering again!",
        "Disaster! {dishes} were all stale. {highlight} had a weird smell. Completely unacceptable!",
        "Appalling quality! {dishes} were swimming in oil. {highlight} was raw inside. Health hazard!",
        "Shocking! {dishes} bore no resemblance to the menu description. {highlight} was inedible. Refund demanded!",
    ]
}

# ============================================
# ENHANCED IMAGE QUERIES
# ============================================

POSITIVE_QUERIES = [
    # Specific Indian dishes - appetizing
    "delicious butter chicken curry",
    "fresh naan bread basket",
    "aromatic biryani rice plate",
    "colorful paneer tikka skewers",
    "steaming dal makhani bowl",
    "golden samosa platter",
    "tandoori chicken platter",
    "creamy korma curry",
    "fragrant pulao rice",
    "crispy dosa breakfast",
    
    # Restaurant presentation
    "indian thali platter",
    "restaurant indian food presentation",
    "gourmet indian cuisine",
    "authentic indian restaurant meal",
    "fresh indian appetizers",
    "colorful indian street food",
    "traditional indian feast",
    "premium indian dining",
    
    # Specific items - high quality
    "fluffy basmati rice",
    "golden fried pakora",
    "vibrant vegetable curry",
    "aromatic masala chai",
    "creamy mango lassi",
    "fresh mint chutney",
    "warm garlic naan",
    "sizzling kebab platter"
]

NEGATIVE_QUERIES = [
    # Burnt/overcooked food
    "burnt pizza crust black",
    "overcooked dry chicken breast",
    "charred burnt meat",
    "blackened burnt toast",
    "burnt food kitchen mistake",
    "overcooked dry rice",
    "scorched burnt vegetables",
    "burnt edges food plate",
    
    # Cold/congealed food
    "congealed gravy cold",
    "cold greasy food plate",
    "solidified oil food",
    "cold fast food burger",
    "cold soggy fries",
    "congealed sauce plate",
    "room temperature food",
    "lukewarm leftover food",
    
    # Poor quality/presentation
    "messy food spill plate",
    "unappetizing food presentation",
    "sloppy restaurant food",
    "food with hair contamination",
    "dirty food plate restaurant",
    "poor quality fast food",
    "disgusting cafeteria food",
    "unappetizing school lunch",
    
    # Spoiled/rotten
    "moldy bread food waste",
    "rotten vegetables spoiled",
    "expired food contamination",
    "decomposed food waste",
    "spoiled dairy products",
    "food poisoning contaminated",
    
    # Undercooked
    "undercooked raw chicken",
    "raw meat pink inside",
    "uncooked dough bread",
    "undercooked pasta hard",
    
    # Greasy/oily
    "greasy oily pizza",
    "excessive oil food plate",
    "dripping grease burger",
    "oil puddle fried food",
    "too much butter sauce",
    
    # Wrong orders/mistakes
    "wrong food order mistake",
    "incorrect restaurant order",
    "missing ingredients food",
    "food delivery disaster",
    "takeout packaging leak",
    "crushed food delivery box"
]

# ============================================
# IMAGE DOWNLOAD FUNCTION
# ============================================
def download_food_image(rating, review_id):
    """Download image from Pexels based on rating"""
    
    # Determine query and folder based on rating
    if rating >= 4:
        queries = POSITIVE_QUERIES
        folder = POSITIVE_FOLDER
        category = "positive"
    else:
        queries = NEGATIVE_QUERIES
        folder = NEGATIVE_FOLDER
        category = "negative"
    
    query = random.choice(queries)
    
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": 5,
        "orientation": "landscape"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            
            if photos:
                # Get random photo from results
                photo = random.choice(photos)
                image_url = photo["src"]["tiny"]
                
                # Download image
                img_response = requests.get(image_url, timeout=10)
                
                if img_response.status_code == 200:
                    filename = f"{category}_{review_id}_{photo['id']}.jpg"
                    filepath = os.path.join(folder, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    return filename
    
    except Exception as e:
        print(f"Image download failed for {review_id}: {e}")
    
    return None

# ============================================
# HELPER FUNCTIONS
# ============================================
def extract_items_from_order(items_json):
    """Extract item names from order JSON"""
    items = json.loads(items_json)
    return [item['name'] for item in items]

def format_dishes(dishes_list):
    """Format dish names for review text"""
    if len(dishes_list) == 1:
        return dishes_list[0]
    elif len(dishes_list) == 2:
        return f"{dishes_list[0]} and {dishes_list[1]}"
    else:
        return f"{', '.join(dishes_list[:-1])}, and {dishes_list[-1]}"

def generate_review_text(rating, dishes_list):
    """Generate review text based on rating and dishes"""
    template = random.choice(REVIEW_TEMPLATES[rating])
    
    dishes_formatted = format_dishes(dishes_list)
    highlight = random.choice(dishes_list)
    
    review = template.format(
        dishes=dishes_formatted,
        highlight=highlight
    )
    
    return review

# ============================================
# GENERATE REVIEWS WITH IMAGES
# ============================================
def generate_customer_reviews(review_percentage=0.35):
    """Generate reviews from historical orders with images"""
    
    reviews = []
    
    # Rating distribution
    rating_weights = {
        5: 0.50,
        4: 0.25,
        3: 0.12,
        2: 0.08,
        1: 0.05
    }
    
    ratings_pool = []
    for rating, weight in rating_weights.items():
        ratings_pool.extend([rating] * int(weight * 100))
    
    print(f"\nGenerating reviews from {len(df_orders)} orders...")
    print(f"Target: {review_percentage*100}% of orders will have reviews\n")
    
    image_download_count = 0
    
    for idx, order in df_orders.iterrows():
        # Only 35% of orders get reviews
        if random.random() > review_percentage:
            continue
        
        # Extract dishes from order
        dishes = extract_items_from_order(order['items'])
        
        # Assign rating
        rating = random.choice(ratings_pool)
        
        # Generate review text
        review_text = generate_review_text(rating, dishes)
        
        # Review date: 1-7 days after order
        order_date = datetime.fromisoformat(order['timestamp'])
        review_date = order_date + timedelta(days=random.randint(1, 7))
        
        # Generate review ID
        review_id = f"REV-{len(reviews) + 1:06d}"
        
        # Determine if review has image
        # Preferable to have images for negative reviews
        has_image = False
        image_filename = None
        
        if rating == 5:
            has_image = random.random() < 0.20
        elif rating == 4:
            has_image = random.random() < 0.15
        elif rating == 3:
            has_image = random.random() < 0.10
        elif rating == 2:
            has_image = random.random() < 0.40
        elif rating == 1:
            has_image = random.random() < 0.60
        
        # Download image if needed
        if has_image:
            image_filename = download_food_image(rating, review_id)
            if image_filename:
                image_download_count += 1
                print(f"[{image_download_count}] Downloaded image for {review_id} (rating: {rating})")
            time.sleep(0.5)  # Rate limiting
        
        review = {
            "review_id": review_id,
            "order_id": order['order_id'],
            "customer_id": order['customer_id'],
            "restaurant_id": order['restaurant_id'],
            "review_text": review_text,
            "rating": rating,
            "review_date": review_date.isoformat(),
            "has_image": has_image,
            "image_filename": image_filename,
            "created_at": review_date.isoformat()
        }
        
        reviews.append(review)
        
        if len(reviews) % 100 == 0:
            print(f"Generated {len(reviews)} reviews...")
    
    df_reviews = pd.DataFrame(reviews)
    df_reviews = df_reviews.sort_values('review_date').reset_index(drop=True)
    df_reviews.to_csv(os.path.join(script_dir, "data", "customer_reviews.csv"), index=False)
    
    # Statistics
    print(f"\n" + "="*60)
    print(f"GENERATION COMPLETE")
    print("="*60)
    print(f"Total reviews: {len(df_reviews)}")
    print(f"Saved to: customer_reviews.csv")
    print(f"\nRating Distribution:")
    print(df_reviews['rating'].value_counts().sort_index())
    print(f"\nReviews with images: {df_reviews['has_image'].sum()} ({df_reviews['has_image'].sum()/len(df_reviews)*100:.1f}%)")
    print(f"Images downloaded: {image_download_count}")
    print(f"Date range: {df_reviews['review_date'].min()} to {df_reviews['review_date'].max()}")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    generate_customer_reviews(review_percentage=0.01)