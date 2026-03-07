import sqlite3

def insert_reviews(reviews):

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    for r in reviews:

        try:

            cursor.execute(
                "INSERT INTO reviews (product, review, review_date) VALUES (?, ?, ?)",
                (r["product"], r["review"], r["date"])
            )

        except sqlite3.IntegrityError:
            # duplicate review
            print("Duplicate skipped")

    conn.commit()
    conn.close()