import sqlite3
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_review(review):

    prompt = f"""
You are a Voice of Customer (VoC) analyst for a consumer electronics company.

Analyze the following customer review.

Return ONLY valid JSON in this format:

{{
  "review": "<original review>",
  "sentiment": "Positive | Neutral | Negative",
  "themes": ["list of themes"],
  "product_action": "action for product engineering team",
  "marketing_action": "action for marketing team",
  "support_action": "action for customer support team"
}}

Guidelines:
- Product actions should suggest product improvements or investigation areas.
- Marketing actions should suggest messaging opportunities or expectations to manage.
- Support actions should suggest documentation, troubleshooting, or response strategies.
- Do NOT suggest replacing the product unless explicitly mentioned by the user.

Themes can include:
Sound Quality
Battery
Comfort
ANC
Call Quality
Connectivity
Build Quality
Price

Review:
{review}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def analyze_reviews():

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    # Only analyze reviews that don't have sentiment yet
    cursor.execute("""
        SELECT id, review 
        FROM reviews
        WHERE sentiment IS NULL
    """)

    rows = cursor.fetchall()

    for r in rows:

        review_id = r[0]
        review_text = r[1]

        print("Analyzing review:", review_id)

        result = analyze_review(review_text)

        try:

            clean = result.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)

            cursor.execute("""
            UPDATE reviews
            SET sentiment = ?, themes = ?, product_action = ?, marketing_action = ?, support_action = ?
            WHERE id = ?
            """, (
                parsed["sentiment"],
                ",".join(parsed["themes"]),
                parsed["product_action"],
                parsed["marketing_action"],
                parsed["support_action"],
                review_id
            ))

            print("Saved analysis for review:", review_id)

        except Exception as e:

            print("Failed to parse JSON for review:", review_id)
            print(result)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    analyze_reviews()