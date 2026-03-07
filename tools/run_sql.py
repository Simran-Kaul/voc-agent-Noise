import sqlite3

def run_sql(query):

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    return rows