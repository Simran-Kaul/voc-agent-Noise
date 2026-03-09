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
Your goal is to extract **product insights from customer feedback**.
Analyze the review and generate **specific, actionable insights for internal teams**.
Return ONLY valid JSON.
Format:
{{
  "sentiment": "Positive | Neutral | Negative",
  "themes": ["theme1","theme2"],
  "product_action": "specific product improvement or investigation tied to the review",
  "marketing_action": "specific messaging adjustment based on the review",
  "support_action": "specific troubleshooting, documentation or FAQ improvement"
}}
Important rules:
1. Actions MUST be based on the review content.
2. Avoid generic statements like:
   - investigate customer expectations
   - gather more feedback
   - manage expectations
3. Product actions should suggest concrete product improvements or validation checks.
4. Marketing actions should suggest messaging changes related to the detected theme.
5. Support actions should suggest FAQ updates, troubleshooting, or guides.
6. If the review is very short, infer the most likely theme and provide a relevant action.
Themes must be chosen ONLY from this list:
Sound Quality
Battery Life
Comfort/Fit
ANC
Call Quality
Connectivity
Build Quality
Price/Value
App Experience
Delivery
Review:
{review}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def analyze_reviews():
    conn = sqlite3.connect("data/reviews.db")
    cursor = conn.cursor()

    # Only analyze reviews that don't have sentiment yet
    cursor.execute("""
        SELECT id, product, review
        FROM reviews
        WHERE sentiment IS NULL
    """)
    rows = cursor.fetchall()

    for r in rows:
        review_id = r[0]
        product = r[1]   # always use product name from DB, never from LLM
        review_text = r[2]

        # skip header junk
        if "ratings and" in review_text.lower():
            continue

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

            print("Saved analysis for review:", review_id, {
                "product": product,
                "sentiment": parsed["sentiment"],
                "themes": parsed["themes"]
            })

        except Exception as e:
            print("Failed to parse JSON for review:", review_id)
            print(result)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    analyze_reviews()