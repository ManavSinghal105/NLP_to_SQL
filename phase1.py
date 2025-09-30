import sqlite3
import os
import google.generativeai as genai
from tabulate import tabulate
import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

if not Path("demo1.db").exists():
    import subprocess, sys
    subprocess.run([sys.executable, "seed_db.py"], check=True)
conn = sqlite3.connect("demo1.db")
cursor = conn.cursor()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it first.")

genai.configure(api_key=api_key)

def nl_to_sql(nl_query):
    prompt = f"""
    You are an assistant that translates natural language to SQL.
    Schema:
    - customers(id, name, city, signup_date)
    - orders(id, customer_id, product, amount, order_date)

    Rules:
    - Always use single quotes for strings.
    - Always make string comparisons case-insensitive (use LOWER()).
    - Always return ONLY the SQL query, nothing else.

    Question: {nl_query}
    SQL Query:
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    sql_query = response.text.strip()

    
    if sql_query.startswith("```"):
        sql_query = sql_query.split("```")[1]
    sql_query = sql_query.replace("sql", "").strip()
    sql_query = sql_query.replace('"', "'")
    sql_query = sql_query.rstrip(";") + ";"

    if not any(keyword in sql_query.lower() for keyword in ["select", "insert", "update", "delete"]):
        return None

    return sql_query

def run_sql(sql_query):
    if sql_query is None:
        return "⚠️ Model did not generate a valid SQL query."

    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        if not rows:
            return "⚠️ No results found."
        col_names = [desc[0] for desc in cursor.description]
        return tabulate(rows, headers=col_names, tablefmt="psql")
    except Exception as e:
        return f"❌ Error running SQL: {e}"

def log_query(question, sql, result):
    with open("query_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.datetime.now()}]\n")
        f.write(f"Q: {question}\n")
        f.write(f"SQL: {sql}\n")
        f.write(f"Result:\n{result}\n")
        f.write("="*50 + "\n")

if __name__ == "__main__":
    print("💬 Ask me questions about the database (type 'exit' to quit)")
    while True:
        question = input("\nYour question: ")
        if question.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        sql = nl_to_sql(question)
        print("Generated SQL:", sql)

        result = run_sql(sql)
        print("Result:\n", result)

        log_query(question, sql, result)
