import os
import sqlite3
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from db_insert import insert_reviews

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

product_name = "Noise Master Buds"

base_url ="https://www.flipkart.com/noise-master-buds-sound-bose-49db-anc-6-mic-enc-44-hr-battery-spatial-audio-bluetooth/product-reviews/itm1cb4f0cb9d57a?pid=ACCHDEX9WH93USFJ&lid=LSTACCHDEX9WH93USFJGYUFXX&aid=overall&certifiedBuyer=false&sortOrder=MOST_RECENT"

all_reviews = []


# check if review already exists in database
def review_exists(review_text):

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM reviews WHERE review = ?",
        (review_text,)
    )

    exists = cursor.fetchone()

    conn.close()

    return exists is not None


for page in range(2, 4):

    url = f"{base_url}&page={page}"

    print("Scraping page:", page)

    result = app.scrape(
        url=url,
        formats=["markdown"]
    )

    content = result.markdown

    # split review sections
    parts = content.split("Verified Purchase")

    stop_scraping = False

    for p in parts:

        if "Review for:" in p:

            lines = [l.strip() for l in p.split("\n") if l.strip()]

            review_text = None
            review_date = None

            for l in lines:

                # capture relative date
                if "ago" in l:
                    review_date = l

                # capture review sentence
                if (
                    len(l) > 40
                    and "Review for:" not in l
                    and "Helpful" not in l
                    and "ago" not in l
                    and "![]" not in l
                ):
                    review_text = l
                    break

            if review_text:

                # stop scraping if review already exists
                if review_exists(review_text):

                    print("Existing review found → stopping further scraping")

                    stop_scraping = True
                    break

                all_reviews.append({
                    "product": product_name,
                    "review": review_text,
                    "date": review_date,
                    "page": page
                })

    if stop_scraping:
        break


print("Total reviews collected:", len(all_reviews))

for r in all_reviews[:5]:
    print("\n", r)


if all_reviews:

    insert_reviews(all_reviews)

    print("Reviews saved to database")

else:

    print("No new reviews found")