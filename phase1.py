import os
import re
from dotenv import load_dotenv

from cache_manager import QueryCache
from context_manager import ContextManager
from db import get_connection, extract_schema
from retriever import SchemaRetriever
from query_engine import configure_gemini, nl_to_sql, run_sql
from validator import repair_sql
from explainer import explain_result
from logger import log_query

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
def normalize_for_cache(enriched_question):
    if "Follow-up question:" in enriched_question:
        return enriched_question.split("Follow-up question:")[-1].strip()
    return enriched_question.strip()
def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)  # remove punctuation
    return text
if __name__ == "__main__":
    context = ContextManager()
    cache = QueryCache()

    print("💬 Ask me questions about the database (type 'exit' to quit)")
    while True:
        question = input("\nYour question: ")
        if question.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        enriched_question = context.build_context_prompt(question)
        cache_key = normalize(normalize_for_cache(enriched_question))
        cached = cache.search(cache_key)
        if cached:
            sql, result = cached
            print("⚡ [CACHE HIT]")
            print("Generated SQL:", sql)
            print("Result:\n", result)

            explanation = explain_result(question, sql, result)
            print("📝 Explanation:", explanation)

            context.add_entry(question, sql, result)
            log_query(question, sql, result + "\nExplanation: " + explanation)
            continue

        sql = nl_to_sql(enriched_question, retriever)
        print("Generated SQL:", sql)

        result = run_sql(cursor, sql)

        if result.startswith("❌ Error"):
            fixed_sql = repair_sql(question, sql, result, schema_info)
            print("🔧 Fixed SQL:", fixed_sql)
            result = run_sql(cursor, fixed_sql)
            sql = fixed_sql  

        print("Result:\n", result)

        explanation = explain_result(question, sql, result)
        print("📝 Explanation:", explanation)

        context.add_entry(question, sql, result)
        cache.add(cache_key, sql, result)
        log_query(question, sql, result + "\nExplanation: " + explanation)
