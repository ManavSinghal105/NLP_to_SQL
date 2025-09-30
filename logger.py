
import datetime

def log_query(question, sql, result, filename="query_log.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.datetime.now()}]\n")
        f.write(f"Q: {question}\n")
        f.write(f"SQL: {sql}\n")
        f.write(f"Result:\n{result}\n")
        f.write("="*50 + "\n")
