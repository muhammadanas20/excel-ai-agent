import streamlit as st
import pandas as pd
import openai
from io import BytesIO

# Set your API key (optional if using secrets manager)
openai.api_key = st.secrets["openai_api_key"]

st.title("📊 Excel Data Refiner with AI")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
prompt = st.text_area("🧠 Ask AI to refine or analyze the data", placeholder="e.g., remove empty rows, summarize column A, etc.")

if uploaded_file and prompt:
    df = pd.read_excel(uploaded_file)

    # Turn DataFrame into plain text
    raw_data = df.to_csv(index=False)

    # Send to OpenAI to process
    response = openai.chat.completions.create(
        model="gpt-4o",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": f"Here is the data:\n{raw_data}\n\nInstruction:\n{prompt}"}
        ]
    )

    # Get the reply (expects CSV table in response)
    ai_reply = response.choices[0].message.content

    try:
        # Parse AI's cleaned data as CSV
        cleaned_df = pd.read_csv(BytesIO(ai_reply.encode()))

        st.success("✅ Data refined successfully!")

        # Display cleaned data
        st.dataframe(cleaned_df)

        # Create Excel file
        output = BytesIO()
        cleaned_df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        # Download button
        st.download_button("📥 Download Cleaned Excel", output.getvalue(), "cleaned_data.xlsx", key="download_excel")
    except Exception as e:
        st.error("⚠️ Could not convert AI reply to Excel. Check the format.")
        st.code(ai_reply)
        st.exception(e)
