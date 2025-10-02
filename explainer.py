import google.generativeai as genai

def explain_result(question, sql, result_text, model_name="gemini-2.0-flash"):
    """
    Generate a human-friendly explanation of SQL result.
    """
    prompt = f"""
    The user asked: {question}
    The SQL executed: {sql}
    The result table was:
    {result_text}

    Please explain the result in 1–2 clear sentences.
    """

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text.strip()
