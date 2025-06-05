import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai

# Setup
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

st.title("📊 Excel AI Assistant")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("🔍 Excel Preview", df.head())
    st.subheader("🤖 Ask AI to Modify Excel Data")
user_instruction = st.text_area("Enter your instruction", 
                                placeholder="E.g., 'Remove blank rows and make a bar chart of sales'")

ai_code = ""  # Keep globally accessible
if st.button("Ask AI"):
    if user_instruction:
        with st.spinner("AI is working..."):
            prompt = f"""You are an expert Python developer. Here's a sample DataFrame:\n\n{df.head().to_string()}\n\nInstruction: {user_instruction}\n\nNow write Python code using pandas/matplotlib to do it. DataFrame is named 'df'. Return only Python code."""

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful code assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )

                ai_code = response['choices'][0]['message']['content']
                st.success("✅ AI Code Generated:")
                st.code(ai_code, language='python')

                st.session_state["ai_code"] = ai_code  # Save to session for later

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("❗ Please enter some instructions.")


    user_instruction = st.text_area("What do you want AI to do with this data?")

    if st.button("Ask AI", key="ask_ai_btn"):
        prompt = f"""You are an expert Python developer. Here's a sample DataFrame:\n\n{df.head().to_string()}\n\nInstruction: {user_instruction}\n\nWrite Python code using pandas/matplotlib to do it. DataFrame is named 'df'. Only output Python code."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Python code assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_code = response['choices'][0]['message']['content']
            st.code(ai_code, language='python')
            st.session_state["ai_code"] = ai_code
        except Exception as e:
            st.error(f"OpenAI Error: {e}")

    if "ai_code" in st.session_state:
        if st.button("▶️ Run the AI Code", key="run_code_btn"):
            try:
                local_vars = {"df": df, "plt": plt}
                exec(st.session_state["ai_code"], {}, local_vars)
                st.success("✅ Code executed.")
                if "df" in local_vars:
                    st.write("🧾 Updated DataFrame", local_vars["df"])
            except Exception as e:
                st.error(f"Error running AI code: {e}")
    # Step 1: Clean Data
    if st.button("🧹 Clean Data"):
        df.dropna(inplace=True)
        df.columns = [col.strip().title() for col in df.columns]
        st.write("✅ Cleaned Data", df)

    # Step 2: Plot Chart
    if st.button("📈 Create Chart"):
        try:
            st.write("Select X and Y Columns")
            x_col = st.selectbox("X Axis", df.columns)
            y_col = st.selectbox("Y Axis", df.columns)

            fig, ax = plt.subplots()
            df.plot(x=x_col, y=y_col, kind='bar', ax=ax)
            st.pyplot(fig)
        except:
            st.warning("Please select valid columns")

    # Step 3: Download Updated Excel
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    st.download_button("📥 Download Cleaned Excel", output.getvalue(), "cleaned_data.xlsx")
from io import BytesIO