import os, re
from datetime import datetime
from dotenv import load_dotenv

from db import get_connection, extract_schema
from retriever import SchemaRetriever
from query_engine import configure_gemini, nl_to_sql, run_sql
from expected import EXPECTED

OUTPUT_FILE = "output.txt"
ACCURACY_REPORT = "accuracy_report.txt"

QUERIES = list(EXPECTED.keys())  # you can also append more test prompts here

def parse_row_count_from_table(table_text: str):
    lines = [ln.strip() for ln in table_text.splitlines() if ln.strip()]
    data_rows = [ln for ln in lines if ln.startswith("|") and not set(ln) <= set("|-+")]
    if len(data_rows) >= 2:
        return len(data_rows) - 1   # minus header row
    return None

def parse_scalar_from_table(table_text: str):
    nums = re.findall(r"\b\d+\b", table_text)
    return nums[-1] if nums else None

def check_case(q: str, result_text: str):
    reasons = []
    exp = EXPECTED.get(q)
    if not exp:
        return True, ["No expectation defined; skipping scoring."]

    ok = True
    if "row_count" in exp:
        rc = parse_row_count_from_table(result_text)
        if rc is None or rc != exp["row_count"]:
            ok = False
            reasons.append(f"Row count {rc} ≠ expected {exp['row_count']}.")

    if "scalar_value" in exp:
        sv = parse_scalar_from_table(result_text)
        if sv is None or str(sv) != str(exp["scalar_value"]):
            ok = False
            reasons.append(f"Scalar value {sv} ≠ expected {exp['scalar_value']}.")

    if "must_include" in exp:
        for token in exp["must_include"]:
            if token not in result_text:
                ok = False
                reasons.append(f"Missing '{token}' in result.")

    return ok, reasons

def write_block(fh, title, content):
    fh.write(f"\n{title}\n")
    fh.write("-" * max(12, len(title)) + "\n")
    fh.write((content or "") + "\n")

def finalize_accuracy_report(results):
    total = sum(1 for q, ok, _ in results if q in EXPECTED)
    correct = sum(1 for q, ok, _ in results if q in EXPECTED and ok)
    pct = (correct / total * 100) if total else 0.0

    with open(ACCURACY_REPORT, "w", encoding="utf-8") as fh:
        fh.write("NL→SQL Accuracy Report\n")
        fh.write("=" * 80 + "\n")
        fh.write(f"Scored cases: {total}\n")
        fh.write(f"Correct:      {correct}\n")
        fh.write(f"Accuracy:     {pct:.1f}%\n")
        fh.write("-" * 80 + "\n\n")
        for q, ok, reasons in results:
            if q not in EXPECTED:
                continue
            status = "✅ PASS" if ok else "❌ FAIL"
            fh.write(f"{status}  {q}\n")
            for r in reasons:
                fh.write(f"   - {r}\n")
            fh.write("\n")

def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not found. Set it in .env or env vars.")

    configure_gemini(api_key)

    DB_NAME = "demo1.db"
    conn = get_connection(DB_NAME)
    cursor = conn.cursor()

    schema_info = extract_schema(DB_NAME)
    retriever = SchemaRetriever(schema_info)

    eval_results = []

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(f"Batch NL→SQL Test Run\nTimestamp: {datetime.now()}\n")
        fh.write("=" * 80 + "\n")

        for i, q in enumerate(QUERIES, start=1):
            fh.write("\n" + "#" * 80 + "\n")
            fh.write(f"CASE {i}\n")
            fh.write("#" * 80 + "\n")

            write_block(fh, "Natural Language Query", q)

            try:
                sql = nl_to_sql(q, retriever)
            except Exception as e:
                write_block(fh, "Generated SQL (error)", f"❌ Error generating SQL: {e}")
                eval_results.append((q, False, [f"Generation error: {e}"]))
                continue

            write_block(fh, "Generated SQL", sql or "⚠️ None")

            try:
                result = run_sql(cursor, sql)
            except Exception as e:
                result = f"❌ Error running SQL: {e}"

            write_block(fh, "Result", result)

            ok, reasons = check_case(q, result)
            eval_results.append((q, ok, reasons))
            status = "✅ PASS" if ok else "❌ FAIL"
            write_block(fh, "Evaluation", status + ("\n" + "\n".join(reasons) if reasons else ""))

            fh.flush()

    finalize_accuracy_report(eval_results)
    print(f"✅ Done.\n- Detailed log: {OUTPUT_FILE}\n- Accuracy:     {ACCURACY_REPORT}")

if __name__ == "__main__":
    main()
