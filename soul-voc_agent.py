import subprocess
from groq import Groq
import os
from dotenv import load_dotenv
from tools.run_sql import run_sql

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -------------------------------
# LOAD AGENT SOUL
# -------------------------------

def load_soul():
    with open("soul.md", "r") as f:
        return f.read()


SOUL = load_soul()


# -------------------------------
# TOOL DEFINITIONS
# -------------------------------

def scrape_reviews():
    print("\nRunning tool: scrape_reviews\n")
    subprocess.run(["python", "tools/flipkart-page.py"])


def generate_report():
    print("\nRunning tool: generate_report\n")
    subprocess.run(["python", "tools/generate_report.py"])


# -------------------------------
# TOOL REGISTRY
# -------------------------------

TOOLS = {
    "scrape_reviews": scrape_reviews,
    "run_sql": run_sql,
    "generate_report": generate_report
}


# -------------------------------
# AGENT DECISION
# -------------------------------

def decide_tool(user_input):

    prompt = f"""
{SOUL}

User request:
{user_input}

You are a tool router.

Return ONLY ONE tool name from the list below:

scrape_reviews
run_sql
generate_report

Rules:

Use run_sql when the user asks about the reviews database.

Database schema:

Table: reviews

Columns:
review TEXT
sentiment TEXT
themes TEXT
scraped_at TIMESTAMP

Examples of run_sql queries:
- how many reviews exist
- list reviews
- show negative reviews
- sentiment distribution
- theme frequency

Use scrape_reviews when the user asks to collect or update reviews.

Use generate_report when the user asks to generate or export a VoC report.

Return ONLY the tool name.
No explanation.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    tool = response.choices[0].message.content.strip().lower()

    for t in TOOLS.keys():
        if t in tool:
            return t

    return tool


# -------------------------------
# AGENT LOOP
# -------------------------------

def run_agent():

    print("\nVoice of Customer Agent Ready\n")

    while True:

        user_input = input("\nAsk the agent: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        tool = decide_tool(user_input)

        print("\nAgent decided to run:", tool)

        if tool in TOOLS:

            if tool == "run_sql":

                # Step 1: LLM generates SQL
                sql_prompt = f"""
Write a SQLite query to answer the user question.

Database schema:

Table: reviews
Columns: review, sentiment, themes, scraped_at

User question:
{user_input}

Rules:
Return ONLY the SQL query.
Do NOT include markdown.
Do NOT include explanations.
Do NOT include ```sql blocks.
"""

                sql_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": sql_prompt}]
                )

                sql_query = sql_response.choices[0].message.content.strip()

                # remove markdown formatting
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

                # ensure only SQL statement remains
                if ";" in sql_query:
                    sql_query = sql_query.split(";")[0] + ";"
                print("\nGenerated SQL:\n", sql_query)

                rows = run_sql(sql_query)

                # Step 2: LLM explains results
                explain_prompt = f"""
User question:
{user_input}

SQL result:
{rows}

Explain the answer conversationally.
"""

                explanation = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": explain_prompt}]
                )

                print("\nAgent:\n")
                print(explanation.choices[0].message.content)

            else:

                result = TOOLS[tool]()

                if result:
                    print("\nAgent:\n")
                    print(result)

        else:
            print("Unknown tool:", tool)


if __name__ == "__main__":
    run_agent()