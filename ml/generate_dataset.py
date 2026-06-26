"""
Synthetic Transaction Dataset Generator
========================================
Generates 50,000+ realistic Indian personal finance transactions and saves
them to ml/data/transactions.csv.

Usage
-----
    python ml/generate_dataset.py
"""
import os
import random
import csv
from datetime import date, timedelta

random.seed(42)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "transactions.csv")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ── Category → Merchant templates ────────────────────────────────────

CATEGORY_MERCHANTS = {
    "Food": [
        ("Swiggy order", 120, 800),
        ("Zomato delivery", 150, 750),
        ("McDonald's", 200, 500),
        ("KFC bucket", 300, 700),
        ("Pizza Hut", 250, 800),
        ("Café Coffee Day", 100, 300),
        ("local restaurant bill", 80, 400),
        ("canteen lunch", 50, 120),
        ("Domino's pizza", 200, 600),
        ("breakfast at hotel", 60, 250),
        ("Haldiram snacks", 80, 300),
        ("biryani house", 120, 400),
        ("college mess fee", 1500, 3000),
        ("tea and snacks", 20, 80),
        ("Barbeque Nation", 500, 1500),
    ],
    "Transport": [
        ("Ola cab", 80, 400),
        ("Uber ride", 90, 500),
        ("Rapido bike", 30, 120),
        ("BMTC bus pass", 200, 600),
        ("IRCTC train ticket", 200, 2000),
        ("metro card recharge", 100, 500),
        ("auto rickshaw", 30, 150),
        ("petrol HP pump", 500, 2000),
        ("Namma Yatri ride", 60, 250),
        ("toll payment fastag", 50, 200),
        ("parking charges", 20, 100),
    ],
    "Healthcare": [
        ("Apollo pharmacy", 200, 1500),
        ("MedPlus medicines", 100, 800),
        ("doctor consultation", 300, 1000),
        ("Manipal Hospital bill", 500, 5000),
        ("dental clinic", 400, 2000),
        ("diagnostic lab test", 300, 2000),
        ("vitamin supplements", 200, 800),
        ("eye checkup", 200, 600),
        ("Practo consultation", 200, 500),
    ],
    "Entertainment": [
        ("Netflix subscription", 149, 649),
        ("Amazon Prime", 179, 179),
        ("Hotstar subscription", 299, 899),
        ("Spotify premium", 119, 119),
        ("PVR movie ticket", 200, 600),
        ("INOX ticket", 180, 550),
        ("Steam game purchase", 500, 2000),
        ("YouTube Premium", 129, 189),
        ("BookMyShow event", 300, 1500),
        ("gaming café", 100, 400),
    ],
    "Education": [
        ("Udemy course", 399, 1299),
        ("Coursera subscription", 500, 2000),
        ("college fee", 10000, 50000),
        ("exam fee", 500, 2000),
        ("stationery Natraj", 50, 300),
        ("notebook purchase", 30, 200),
        ("textbook Amazon", 200, 1500),
        ("coaching institute fee", 2000, 8000),
        ("Unacademy subscription", 600, 2400),
    ],
    "Shopping": [
        ("Amazon purchase", 200, 3000),
        ("Flipkart order", 150, 2500),
        ("Myntra clothes", 300, 2000),
        ("Ajio fashion", 400, 2500),
        ("Nykaa cosmetics", 200, 1500),
        ("Meesho order", 100, 800),
        ("D-Mart grocery", 300, 2000),
        ("BigBasket order", 400, 2000),
        ("Blinkit order", 200, 1000),
        ("Decathlon sports", 500, 3000),
    ],
    "Utilities": [
        ("BESCOM electricity bill", 400, 2000),
        ("BWSSB water bill", 100, 400),
        ("Airtel postpaid", 299, 799),
        ("Jio recharge", 149, 599),
        ("BSNL broadband", 400, 800),
        ("gas cylinder booking", 800, 1100),
        ("ACT Fibernet", 499, 999),
        ("BBMP property tax", 1000, 5000),
    ],
    "Investments": [
        ("Zerodha brokerage", 1000, 10000),
        ("Groww SIP", 500, 5000),
        ("mutual fund SIP HDFC", 1000, 5000),
        ("fixed deposit SBI", 5000, 50000),
        ("LIC premium", 2000, 10000),
        ("PPF deposit", 1000, 10000),
        ("gold purchase", 5000, 50000),
        ("NPS contribution", 1000, 5000),
    ],
    "Travel": [
        ("IndiGo flight", 2000, 10000),
        ("Air India ticket", 3000, 15000),
        ("OYO hotel booking", 500, 3000),
        ("MakeMyTrip hotel", 1000, 6000),
        ("Airbnb stay", 1500, 8000),
        ("Goibibo trip", 2000, 12000),
        ("train travel IRCTC", 500, 4000),
        ("travel insurance", 300, 1500),
    ],
    "Miscellaneous": [
        ("ATM withdrawal", 500, 5000),
        ("gift purchase", 200, 2000),
        ("donation charity", 100, 1000),
        ("newspaper subscription", 50, 200),
        ("haircut salon", 100, 500),
        ("laundry service", 100, 500),
        ("mobile repair", 200, 2000),
        ("unknown merchant", 100, 1000),
    ],
}

# ── Generation ────────────────────────────────────────────────────────

START_DATE = date(2022, 1, 1)
END_DATE = date(2024, 12, 31)
NUM_USERS = 20
TARGET_ROWS = 55_000

rows = []
user_ids = list(range(1, NUM_USERS + 1))

while len(rows) < TARGET_ROWS:
    user_id = random.choice(user_ids)
    category = random.choice(list(CATEGORY_MERCHANTS.keys()))
    merchant, min_amt, max_amt = random.choice(CATEGORY_MERCHANTS[category])
    amount = round(random.uniform(min_amt, max_amt), 2)
    days_gap = random.randint(0, (END_DATE - START_DATE).days)
    txn_date = START_DATE + timedelta(days=days_gap)
    payment_mode = random.choice(["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"])

    rows.append({
        "user_id": user_id,
        "date": txn_date.isoformat(),
        "amount": amount,
        "description": merchant,
        "category": category,
        "payment_mode": payment_mode,
    })

# Sort by date
rows.sort(key=lambda r: r["date"])

# Write CSV
with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["user_id", "date", "amount", "description", "category", "payment_mode"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Dataset generated: {len(rows)} transactions -> {OUTPUT_PATH}")
