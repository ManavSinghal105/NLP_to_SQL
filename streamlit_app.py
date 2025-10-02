import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/ask"   # Make sure FastAPI is running

st.set_page_config(page_title="NL2SQL Demo", layout="wide")
st.title("💬 Natural Language to SQL")

# ----------------------------
# Query Input
# ----------------------------
question = st.text_input("Enter your question about the database:")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"question": question})
            if response.status_code != 200:
                st.error(f"API error: {response.status_code}")
            else:
                data = response.json()

                # Show SQL
                st.subheader("Generated SQL")
                st.code(data.get("sql", ""), language="sql")

                # Show results
                st.subheader("Results")
                json_result = data.get("json_result", [])
                if json_result:
                    df = pd.DataFrame(json_result)
                    st.dataframe(df)

                    # Optional: if numeric column exists, show chart
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) >= 1:
                        st.subheader("Chart")
                        st.bar_chart(df.set_index(df.columns[0])[numeric_cols])
                else:
                    st.write(data.get("ascii_result", "⚠️ No results."))

                # Explanation
                st.subheader("Explanation")
                st.write(data.get("explanation", ""))
        except Exception as e:
            st.error(f"❌ Exception: {e}")
