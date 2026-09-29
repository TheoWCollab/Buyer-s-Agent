import requests
import re
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).parent

RESULTS_FILE = BASE_DIR / "results.json"

HISTORY_FILE = BASE_DIR / "history.csv"

PRODUCT_NAME = "Dior Prestige La Creme 50ml"

PRODUCT_URL = (
    "https://www.myer.com.au/p/"
    "dior-prestige-la-creme-texture-essentielle-50ml"
)

TARGET_COST = 580.00

AECOM_DISCOUNT = 0.06

TRAVEL_MODE = True

PROMOTION_KEYWORDS = [
    "gift with purchase",
    "bonus gift",
    "exclusive offer",
    "beauty event",
    "beauty sale",
    "spend and save",
    "special offer"
]

# ==========================================
# DOWNLOAD PAGE
# ==========================================

response = requests.get(
    PRODUCT_URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

html = response.text

# ==========================================
# EXTRACT PRICE
# ==========================================

price_match = re.search(
    r'"price":(\d+)',
    html
)

if not price_match:
    print("❌ Unable to locate product price")
    raise SystemExit()

price = float(price_match.group(1))

# ==========================================
# CALCULATIONS
# ==========================================

gift_card_saving = price * AECOM_DISCOUNT

cash_paid = (
    price
    - gift_card_saving
)

trs_refund = price / 11

travel_net_cost = (
    cash_paid
    - trs_refund
)

# ==========================================
# PROMOTION SCAN
# ==========================================

promotion_results = []

html_lower = html.lower()

for keyword in PROMOTION_KEYWORDS:

    position = html_lower.find(keyword)

    if position != -1:

        start = max(0, position - 250)
        end = position + 500

        snippet = html[start:end]

        promotion_results.append(
            {
                "keyword": keyword,
                "snippet": snippet
            }
        )

# ==========================================
# PROMO CODE EXTRACTION
# ==========================================

promo_patterns = [

    r'promo code[:\s]+([A-Z0-9]+)',

    r'voucher code[:\s]+([A-Z0-9]+)',

    r'code[:\s]+([A-Z0-9]{4,20})',

    r'coupon code[:\s]+([A-Z0-9]+)'
]

codes_found = set()

for pattern in promo_patterns:

    matches = re.findall(
        pattern,
        html,
        flags=re.IGNORECASE
    )

    for match in matches:

        if len(match) >= 4:
            codes_found.add(match)

# ==========================================
# REPORT
# ==========================================

print()
print("=" * 60)
print("MYER DIOR BUYER AGENT")
print("=" * 60)

print(f"Product               : {PRODUCT_NAME}")
print(f"Current Myer Price    : ${price:.2f}")

print("\nSavings")

print(
    f"AECOM Discount (6%)   : -${gift_card_saving:.2f}"
)

print(
    f"Cash Paid             : ${cash_paid:.2f}"
)

if TRAVEL_MODE:

    print(
        f"TRS Refund Estimate   : -${trs_refund:.2f}"
    )

    print(
        f"Travel Net Cost       : ${travel_net_cost:.2f}"
    )

print(
    f"\nTarget Cost           : ${TARGET_COST:.2f}"
)

# ==========================================
# PROMOTIONS
# ==========================================

print("\n" + "=" * 60)
print("PROMOTION SCAN")
print("=" * 60)

if promotion_results:

    for item in promotion_results:

        print()
        print(f"Keyword: {item['keyword']}")
        print("-" * 40)

        cleaned = re.sub(
            r"\s+",
            " ",
            item["snippet"]
        )

        print(cleaned[:400])

else:

    print("No promotion keywords detected.")

# ==========================================
# PROMO CODES
# ==========================================

print("\n" + "=" * 60)
print("PROMO CODE SCAN")
print("=" * 60)

if codes_found:

    for code in sorted(codes_found):

        print(f"Code Found: {code}")

else:

    print("No promo codes detected.")

# ==========================================
# RECOMMENDATION
# ==========================================

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)

if cash_paid <= TARGET_COST:

    print("✅ BUY NOW")

elif (
    TRAVEL_MODE and
    travel_net_cost <= TARGET_COST
):

    print("✈️ BUY BEFORE OVERSEAS TRIP")

else:

    difference = (
        cash_paid
        - TARGET_COST
    )

    print("⏳ WAIT")
    print(
        f"${difference:.2f} above target"
    )

print()

# ==========================================
# SAVE RESULTS JSON
# ==========================================

import json
from datetime import datetime

if cash_paid <= TARGET_COST:

    recommendation = "BUY NOW"

elif (
    TRAVEL_MODE and
    travel_net_cost <= TARGET_COST
):

    recommendation = "BUY BEFORE OVERSEAS TRIP"

else:

    recommendation = "WAIT"

result = {
    "product": PRODUCT_NAME,
    "price": round(price, 2),
    "cash_paid": round(cash_paid, 2),
    "travel_net_cost": round(travel_net_cost, 2),
    "target_cost": TARGET_COST,
    "recommendation": recommendation,
    "last_updated": datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )
}

with open(RESULTS_FILE, "w") as f:
    json.dump(result, f, indent=2)

print("✅ results.json updated")

import csv
from datetime import datetime

with open(HISTORY_FILE, "a", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        datetime.now().strftime("%Y-%m-%d"),
        price,
        cash_paid,
        travel_net_cost
    ])

# ==========================================
# Debug Messages
# ==========================================

print("✅ history.csv updated")
print("✅ Buyer Agent completed")