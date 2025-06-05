import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
import streamlit as st
from openai import OpenAI

# Load API key from secrets
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

st.title("Excel Data Refiner & Chart Generator")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Raw Data")
    st.write(df)

    user_prompt = st.text_area("Enter your request (e.g., 'Clean missing data and plot sales by region')")

    if st.button("Ask AI", key="ask_ai_button"):
        with st.spinner("Thinking..."):
            # Create chat messages
            messages = [
                {"role": "system", "content": "You are a helpful assistant who analyzes and cleans Excel data."},
                {"role": "user", "content": f"Data:\n{df.head(10).to_string()}\n\nRequest:\n{user_prompt}"}
            ]

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.5,
                )

                reply = response.choices[0].message.content
                st.markdown("### AI Response")
                st.write(reply)

            except Exception as e:
                st.error(f"Error from OpenAI: {str(e)}")
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