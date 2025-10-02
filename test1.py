from fastapi import FastAPI
from pydantic import BaseModel

import os
import re
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from cache_manager import QueryCache
from context_manager import ContextManager
from db import get_connection, extract_schema
from retriever import SchemaRetriever
from query_engine import configure_gemini, nl_to_sql, run_sql
from validator import repair_sql
from explainer import explain_result
from logger import log_query

# ----------------------------
# Setup
# ----------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in .env")

configure_gemini(api_key)

DB_NAME = "demo1.db"
conn = get_connection(DB_NAME)
cursor = conn.cursor()
schema_info = extract_schema(DB_NAME)
retriever = SchemaRetriever(schema_info)

context = ContextManager()
cache = QueryCache()

# ----------------------------
# Helpers
# ----------------------------
def normalize_for_cache(enriched_question):
    if "Follow-up question:" in enriched_question:
        return enriched_question.split("Follow-up question:")[-1].strip()
    return enriched_question.strip()

def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)  # remove punctuation
    return text

# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI(title="NL2SQL API", version="1.0")

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(request: QueryRequest):
    question = request.question

    # --- Enrich with context ---
    enriched_question = context.build_context_prompt(question)
    cache_key = normalize(normalize_for_cache(enriched_question))

    # --- Check cache ---
    cached = cache.search(cache_key)
    if cached:
        sql, (json_result, ascii_result) = cached
        explanation = explain_result(question, sql, ascii_result)
        context.add_entry(question, sql, ascii_result)
        log_query(question, sql, ascii_result + "\nExplanation: " + explanation)
        return {
            "sql": sql,
            "json_result": json_result,   # 👈 structured JSON for Streamlit
            "ascii_result": ascii_result, # 👈 for logs/debug
            "explanation": explanation,
            "cached": True
        }

    # --- Generate SQL ---
    sql = nl_to_sql(enriched_question, retriever)
    json_result, ascii_result = run_sql(cursor, sql)


    # --- Repair if needed ---
    if isinstance(ascii_result, str) and ascii_result.startswith("❌ Error"):
        fixed_sql = repair_sql(question, sql, ascii_result, schema_info)
        json_result, ascii_result = run_sql(cursor, fixed_sql)
        sql = fixed_sql   

    # --- Explanation ---
    explanation = explain_result(question, sql, ascii_result)

    # --- Save ---
    context.add_entry(question, sql, ascii_result)
    cache.add(cache_key, sql, (json_result, ascii_result))
    log_query(question, sql, ascii_result + "\nExplanation: " + explanation)

    return {
        "sql": sql,
        "json_result": json_result,
        "ascii_result": ascii_result,
        "explanation": explanation,
        "cached": False
    }
