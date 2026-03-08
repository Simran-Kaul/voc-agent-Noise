import os
import sqlite3
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from db_insert import insert_reviews

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
conn = sqlite3.connect("data/reviews.db")
cursor = conn.cursor()

product_name = "Noise Master Buds"

base_url = "https://www.flipkart.com/noise-master-buds-sound-bose-49db-anc-6-mic-enc-44-hr-battery-spatial-audio-bluetooth/product-reviews/itm1cb4f0cb9d57a?pid=ACCHDEX9WH93USFJ&lid=LSTACCHDEX9WH93USFJGYUFXX&aid=overall&certifiedBuyer=false&sortOrder=MOST_RECENT"
all_reviews = []

import datetime

from collections import Counter
import datetime

from collections import Counter
import datetime
import os

def log_delta(new_reviews):

    os.makedirs("reports", exist_ok=True)

    product = new_reviews[0]["product"]

    sentiments = []
    themes = []

    for r in new_reviews:

        if r.get("sentiment"):
            sentiments.append(r["sentiment"])

        if r.get("themes"):
            themes.extend(r["themes"].split(","))

    sentiment_count = Counter(sentiments)
    theme_count = Counter(themes)

    file_path = "reports/weekly_delta_report.md"

    write_mode = "a" if os.path.exists(file_path) else "w"

    with open(file_path, write_mode) as f:

        if write_mode == "w":
            f.write("# Weekly Review Delta\n\n")
            f.write(f"Run Date: {datetime.datetime.now()}\n\n")

        f.write(f"## {product}\n\n")

        f.write(f"New Reviews Captured: {len(new_reviews)}\n\n")

        if sentiment_count:
            f.write("### Sentiment Distribution\n")
            for k, v in sentiment_count.items():
                f.write(f"{k}: {v}\n")

        if theme_count:
            f.write("\n### Emerging Themes\n")
            for theme, count in theme_count.most_common(3):
                f.write(f"{theme}: {count}\n")

        f.write("\n### Sample Reviews\n")

        for r in new_reviews[:5]:
            f.write(f"- {r['review'][:200]}\n")

        f.write("\n\n")
        
# check if review already exists in database

def review_exists(review_text, ):

    cursor.execute(
        "SELECT 1 FROM reviews WHERE review = ?",
        (review_text,)
    )

    return cursor.fetchone() is not None

import time

def scrape_with_retry(url, retries=3):

    for attempt in range(retries):

        result = app.scrape(
            url=url,
            formats=["markdown"]
        )

        content = result.markdown

        # detect Flipkart repair page
        if "Just a quick repair needed" in content:
            print(f"Flipkart repair page detected → retry {attempt+1}/{retries}")

            time.sleep(8)
            continue

        return content

    print("Failed after retries")
    return None


page = 1

while True:
    duplicate_count = 0
    url = f"{base_url}&page={page}"

    print("Scraping page:", page)

    content = scrape_with_retry(url)

    if content is None:
        print("Skipping blocked page")
        page += 1
        continue

    print(url)

    parts = content.split("Verified Purchase")

    page_reviews = 0
    stop_scraping = False

    for p in parts:

        if "Review for:" in p:

            lines = [l.strip() for l in p.split("\n") if l.strip()]

            review_text = None
            review_date = None

            for l in lines:

               
                    
                if "ago" in l:
                    review_date = l

                if (
                    len(l) > 10
                    and "Review for:" not in l
                    and "Helpful" not in l
                    and "ago" not in l
                    and "![]" not in l
                ):
                    review_text = l
                    break

            if review_text:

                if review_exists(review_text):

                    duplicate_count += 1

                    print(f"Duplicate detected ({duplicate_count})")

                    if duplicate_count >= 3:
                        print("Multiple existing reviews detected → stopping scraping")
                        stop_scraping = True
                        break

                    continue

                all_reviews.append({
                    "product": product_name,
                    "review": review_text,
                    "date": review_date,
                    "page": page
                })

                page_reviews += 1

    print(f"Reviews found on page {page}: {page_reviews}")
    
    if stop_scraping:
        break

    if page_reviews == 0:
        print("No reviews found → reached last page")
        break
    
    time.sleep(3)
    page += 1


print("Total reviews collected:", len(all_reviews))

for r in all_reviews[:5]:
    print("\n", r)


if all_reviews:

    insert_reviews(all_reviews)

    log_delta(all_reviews)

    print("Reviews saved to database")

else:

    print("No new reviews found")
conn.close()