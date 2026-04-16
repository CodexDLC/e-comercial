import json
import uuid
import random
from datetime import datetime, timedelta

users = [2, 3, 4, 5]
products = [
    {"id": 1, "price": 5.99},
    {"id": 2, "price": 2.50},
    {"id": 3, "price": 3.25},
    {"id": 4, "price": 60.00},
    {"id": 5, "price": 4.50},
    {"id": 6, "price": 3.00},
    {"id": 7, "price": 6.20},
    {"id": 8, "price": 8.99},
    {"id": 9, "price": 9.50},
    {"id": 10, "price": 2.20},
    {"id": 11, "price": 4.75},
    {"id": 12, "price": 1.80},
]

statuses = ["delivered", "shipped", "processing", "pending"]
addresses = [
    "London, Baker St, 221B",
    "Oxford, High St, 10",
    "Cambridge, Trinity St, 5",
    "Manchester, Piccadilly Gardens, 1",
    "Bristol, Park St, 12",
    "York, Shambles, 4",
    "Edinburgh, Royal Mile, 100",
]

orders = []
order_items = []

base_date = datetime(2026, 4, 16)

for i in range(25):
    # Random date in last 45 days
    days_back = random.randint(0, 45)
    order_date = (base_date - timedelta(days=days_back)).replace(hour=random.randint(9, 20), minute=random.randint(0, 59))
    
    order_id = str(uuid.uuid4())
    user_id = random.choice(users)
    status = random.choice(statuses) if days_back < 5 else "delivered"
    
    # Random items (1-3 items)
    current_order_items = random.sample(products, random.randint(1, 4)) # More items
    total_price = 0
    
    for item in current_order_items:
        qty = random.randint(1, 3)
        price = float(item["price"])
        line_total = price * qty
        total_price += line_total
        
        order_items.append({
            "model": "orders.orderitem",
            "fields": {
                "order": order_id,
                "product": item["id"],
                "quantity": qty,
                "price": f"{price:.2f}"
            }
        })
        
    orders.append({
        "model": "orders.order",
        "pk": order_id,
        "fields": {
            "id": order_id,
            "user": user_id,
            "status": status,
            "total_price": f"{total_price:.2f}",
            "shipping_address": random.choice(addresses),
            "contact_phone": f"+44 7{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(10, 99)}",
            "created_at": order_date.isoformat() + "Z",
            "updated_at": order_date.isoformat() + "Z"
        }
    })

with open("orders_gen.json", "w") as f:
    json.dump(orders, f, indent=2)

with open("order_items_gen.json", "w") as f:
    json.dump(order_items, f, indent=2)

# Generate reviews
reviews = []
for i in range(20):
    review_date = (base_date - timedelta(days=random.randint(0, 40)))
    reviews.append({
        "model": "reviews.review",
        "fields": {
            "user": random.choice(users),
            "product": random.choice(products)["id"],
            "rating": random.randint(3, 5),
            "comment": random.choice([
                "Excellent product, matches description perfectly.",
                "Quality is good, but shipping took a bit longer than expected.",
                "Best purchase this year! Highly recommend to everyone.",
                "Okay product for the price.",
                "Stellar quality, very impressed.",
            ]),
            "is_active": True,
            "created_at": review_date.isoformat() + "Z",
            "updated_at": review_date.isoformat() + "Z"
        }
    })

with open("reviews_gen.json", "w") as f:
    json.dump(reviews, f, indent=2)

print("Generated 25 orders and 20 reviews.")
