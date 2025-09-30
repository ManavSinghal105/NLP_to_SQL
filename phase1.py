import os
from dotenv import load_dotenv

from db import get_connection, extract_schema
from retriever import SchemaRetriever
from query_engine import configure_gemini, nl_to_sql, run_sql
from logger import log_query

# --- Load env vars ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in .env")

configure_gemini(api_key)

# --- Setup DB + Retriever ---
conn = get_connection("demo1.db")
cursor = conn.cursor()
schema_info = extract_schema("demo1.db")
retriever = SchemaRetriever(schema_info)

# --- Interactive Loop ---
if __name__ == "__main__":
    print("💬 Ask me questions about the database (type 'exit' to quit)")
    while True:
        question = input("\nYour question: ")
        if question.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        sql = nl_to_sql(question, retriever)
        print("Generated SQL:", sql)

        result = run_sql(cursor, sql)
        print("Result:\n", result)

        log_query(question, sql, result)
