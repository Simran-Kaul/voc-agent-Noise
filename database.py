import sqlite3

def init_db():

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        review TEXT UNIQUE,
        review_date TEXT,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sentiment TEXT,
        themes TEXT,
        product_action TEXT,
        marketing_action TEXT,
        support_action TEXT
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()