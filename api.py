# api.py
import os
from fastapi import FastAPI, Query
from pydantic import BaseModel
from dotenv import load_dotenv

from db import get_connection, extract_schema
from retriever import SchemaRetriever
from query_engine import configure_gemini, nl_to_sql, run_sql
from validator import repair_sql
from explainer import explain_result
from logger import log_query
from context_manager import ContextManager
from cache_manager import QueryCache

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in .env")

configure_gemini(api_key)

# --- Setup ---
DB_NAME = "demo1.db"
conn = get_connection(DB_NAME)
cursor = conn.cursor()
schema_info = extract_schema(DB_NAME)
retriever = SchemaRetriever(schema_info)

context = ContextManager()
cache = QueryCache()

# --- FastAPI App ---
app = FastAPI(title="NL2SQL API", version="1.0")

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(request: QueryRequest):
    question = request.question

    # Step 0: Check cache
    cached = cache.search(question)
    if cached:
        sql, result = cached
        explanation = explain_result(question, sql, result)
        return {"sql": sql, "result": result, "explanation": explanation, "cached": True}

    # Step 1: Build context
    enriched_question = context.build_context_prompt(question)

    # Step 2: Generate SQL
    sql = nl_to_sql(enriched_question, retriever)

    # Step 3: Run SQL
    result = run_sql(cursor, sql)

    # Step 4: Repair if needed
    if result.startswith("❌ Error"):
        fixed_sql = repair_sql(question, sql, result, schema_info)
        result = run_sql(cursor, fixed_sql)
        sql = fixed_sql

    # Step 5: Explanation
    explanation = explain_result(question, sql, result)

    # Step 6: Log + Cache + Context
    log_query(question, sql, result + "\nExplanation: " + explanation)
    cache.add(question, sql, result)
    context.add_entry(question, sql, result)

    return {"sql": sql, "result": result, "explanation": explanation, "cached": False}
