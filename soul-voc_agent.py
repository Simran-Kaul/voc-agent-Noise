import sqlite3
import subprocess
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------------
# TOOL FUNCTIONS
# -----------------------------

def run_sql(query):

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    return rows


def scrape_reviews():

    print("Running scraper...")
    subprocess.run(["python", "tools/flipkart-page.py"])


def analyze_reviews():

    print("Running analysis...")
    subprocess.run(["python", "tools/analyze_reviews.py"])


def generate_report():

    print("Generating report...")
    subprocess.run(["python", "tools/generate_report.py"])


# -----------------------------
# AGENT REASONING
# -----------------------------

def decide_action(question):

    prompt = f"""
You are a Voice of Customer intelligence agent.

Your job is to decide how to answer the user's question.

Available actions:

run_sql → retrieve data from reviews database  
scrape_reviews → collect latest reviews  
analyze_reviews → analyze unanalyzed reviews  
generate_report → create VoC reports  

Database schema:

Table: reviews

Columns:
review
sentiment
themes
product_action
marketing_action
support_action
scraped_at

User question:
{question}

Return ONLY JSON:

{{
"action": "...",
"sql": "..."
}}

If action is run_sql, provide a SQL query.
Otherwise sql should be empty.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()

    import json
    return json.loads(result)


# -----------------------------
# RESPONSE GENERATION
# -----------------------------

def generate_answer(question, data):

    prompt = f"""
You are a Voice of Customer analyst.

User question:
{question}

Database data:
{data}

Answer conversationally.

Provide:
• Key insights
• Themes observed
• Suggested action for product/marketing/support teams

Use only the provided data.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -----------------------------
# AGENT LOOP
# -----------------------------

def run_agent():

    print("\nVoice of Customer Agent Ready\n")

    while True:

        question = input("\nAsk the agent: ")

        if question.lower() in ["exit", "quit"]:
            break

        decision = decide_action(question)

        action = decision["action"]
        sql = decision["sql"]

        print("\nAgent decision:", action)

        if action == "run_sql":

            data = run_sql(sql)

            answer = generate_answer(question, data)

            print("\nAgent:\n")
            print(answer)

        elif action == "scrape_reviews":

            scrape_reviews()

        elif action == "analyze_reviews":

            analyze_reviews()

        elif action == "generate_report":

            generate_report()

        else:

            print("Unknown action")


if __name__ == "__main__":
    run_agent()