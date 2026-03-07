import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_recent_reviews():

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT review, sentiment, themes
    FROM reviews
    ORDER BY scraped_at DESC
    LIMIT 50
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def answer_question(question):

    data = get_recent_reviews()

    formatted = "\n".join(
    [f"- {r[0]} (Sentiment: {r[1]}, Themes: {r[2]})" for r in data]     
    )

    prompt = f"""
You are a Voice of Customer analyst helping product and marketing teams.

You are a conversational AI agent helping product and marketing teams
understand customer feedback.

Answer naturally as if speaking to a product manager.
Use ONLY the provided review data.

Use ONLY the customer review data provided.

Customer Reviews:
{formatted}

User Question:
{question}

Your response should:
• Be conversational
• Provide the TOP 3 insights
• Explain WHY they matter
• Suggest what the team should do

Example style:

"From the recent customer feedback, three things stand out:

1. Sound Quality is the strongest positive driver
Customers consistently praise the sound clarity and bass.

2. Battery expectations are slightly misaligned
Several users mention shorter battery life during heavy usage.

3. Call quality needs improvement
Some reviews highlight microphone issues during calls.

For marketing, the biggest opportunity is to emphasize the Bose sound collaboration while setting clearer expectations around battery performance."
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    question = input("Ask question: ")

    result = answer_question(question)

    print("\nInsights:\n")
    print(result)