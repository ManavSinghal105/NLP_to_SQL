class ContextManager:
    def __init__(self):
        self.history = []  

    def add_entry(self, question, sql, result):
        """Save a new query interaction to history."""
        self.history.append({
            "question": question,
            "sql": sql,
            "result": result
        })

    def get_last(self):
        """Get the most recent query context."""
        if not self.history:
            return None
        return self.history[-1]

    def build_context_prompt(self, current_question, window=3):
        """
        Build prompt using the last N turns (default 3).
        """
        if not self.history:
            return current_question

        # take last `window` turns
        recent_history = self.history[-window:]

        context_text = "\n".join(
        f"Q: {h['question']}\nSQL: {h['sql']}\nResult: {h['result']}\n"
        for h in recent_history
    )

        enriched = f"""
    Previous conversation:
        {context_text}

    Follow-up question: {current_question}
    """
        return enriched

