import requests
import time

API_URL = "http://127.0.0.1:8000/ask"

# Define queries and golden answers (expected SQL or result keywords)
queries_with_golden = [
    ("Show all customers", "Alice"),
    ("List all the products purchased", "Laptop"),
    ("Show orders with amount greater than 100", "Laptop"),
    ("Get all customer names in alphabetical order", "Alice"),
    ("Show customers from New York", "Charlie"),
    ("Which customer purchased 'Phone'?", "Bob"),
    ("Show orders along with customer city", "San Francisco"),
    ("What is the total number of customers?", "3"),
    ("How many orders were placed in January 2024?", "0"),
    ("List customers whose name starts with 'A'", "Alice"),
    # hallucination tests
    ("Show me the email addresses of customers", "❌"),
    ("List all suppliers", "❌"),
    ("Get total sales per region", "❌")
]

success_count = 0
correct_count = 0
total = len(queries_with_golden)

with open("test_results.txt", "w", encoding="utf-8") as f:
    for i, (q, golden) in enumerate(queries_with_golden, 1):
        payload = {"question": q}
        try:
            response = requests.post(API_URL, json=payload)
            data = response.json()
        except Exception as e:
            data = {"sql": "", "result": f"❌ Request failed: {e}", "explanation": "", "cache": False}

        sql = data.get("sql", "❌ No SQL returned")
        result = data.get("result", "❌ No result")
        explanation = data.get("explanation", "❌ No explanation")
        cache_hit = str(data.get("cache", False))

        # Log results
        f.write("\n" + "#"*80 + f"\nCASE {i}\n" + "#"*80 + "\n")
        f.write("Natural Language Query\n----------------------\n")
        f.write(q + "\n\n")

        f.write("Generated SQL\n-------------\n")
        f.write(sql + "\n\n")

        f.write("Result\n------------\n")
        f.write(result + "\n\n")

        f.write("Explanation\n------------\n")
        f.write(explanation + "\n\n")

        f.write("Cache Hit: " + cache_hit + "\n")
        f.write("Golden Expectation: " + golden + "\n")

        # Evaluation metrics
        if not result.startswith("❌ Error"):
            success_count += 1
        if golden != "❌" and golden.lower() in result.lower():
            correct_count += 1
        if golden == "❌" and "no such" in result.lower():
            correct_count += 1

        f.write("\n\n")

        # Pause after every 3 queries to respect Gemini rate limit
        if i % 3 == 0:
            print(f"⏳ Sleeping 10s after {i} queries...")
            time.sleep(10)

# Final stats
with open("test_results.txt", "a", encoding="utf-8") as f:
    f.write("\n" + "="*80 + "\n")
    f.write(f"Total Queries: {total}\n")
    f.write(f"Success Rate: {success_count/total:.2%}\n")
    f.write(f"Accuracy Rate: {correct_count/total:.2%}\n")
    f.write("="*80 + "\n")

print(f"✅ Finished testing {total} queries. Results saved to test_results.txt")
