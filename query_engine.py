import google.generativeai as genai
from tabulate import tabulate

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def nl_to_sql(nl_query, retriever, model_name="gemini-2.0-flash"):
    """Translate natural language to SQL using Gemini + schema retriever."""
    relevant_schema = retriever.retrieve(nl_query)
    schema_text = "\n".join(relevant_schema)

    prompt = f"""
    You are an assistant that translates natural language to SQL.
    Use only the following schema:

    {schema_text}

    Rules:
    - Always use single quotes for strings.
    - Always make string comparisons case-insensitive (use LOWER()).
    - Do NOT include explanations or markdown fences (```) in the output.
    - Only return a valid SQL query.

    Question: {nl_query}
    SQL Query:
    """

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    sql_query = response.text.strip()

    # --- Cleanup ---
    if "```" in sql_query:
        sql_query = sql_query.replace("```sql", "").replace("```", "")
    sql_query = sql_query.strip()
    if not sql_query.endswith(";"):
        sql_query += ";"

    return sql_query

def run_sql(cursor, sql_query):
    """Run SQL query against DB cursor and format results."""
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
