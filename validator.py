import google.generativeai as genai

def repair_sql(question, sql, error_message, schema_info, model_name="gemini-2.0-flash"):
    """
    Ask Gemini to fix SQL query based on error message and schema.
    """
    prompt = f"""
    You are an assistant that fixes invalid SQL queries.
    
    Schema:
    {schema_info}

    User question:
    {question}

    The model previously generated this SQL:
    {sql}

    But it failed with error:
    {error_message}

    Please return a corrected SQL query.
    Rules:
    - Use only valid columns and tables from schema
    - Do not return explanations or markdown fences
    - Only return a valid SQL query
    """

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    fixed_sql = response.text.strip()

    if "```" in fixed_sql:
        fixed_sql = fixed_sql.replace("```sql", "").replace("```", "")
    return fixed_sql.strip()
