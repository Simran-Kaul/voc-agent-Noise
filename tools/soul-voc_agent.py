from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

# connect SQLite
db = SQLDatabase.from_uri("sqlite:///data/reviews.db")

# Groq model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# create SQL agent
agent = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True
)

print("VoC Agent Ready\n")

while True:

    query = input("You: ")

    if query.lower() == "exit":
        break

    response = agent.invoke({"input": query})

    print("\nAgent:", response["output"], "\n")