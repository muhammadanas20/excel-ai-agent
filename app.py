import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import time

# Configure page
st.set_page_config(
    page_title="📊 Excel Data Refiner with AI (OpenRouter)",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Excel Data Refiner with AI (OpenRouter)")
    st.caption("Upload an Excel file and let AI help clean, transform, or analyze your data")

    # OpenRouter configuration
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    if not OPENROUTER_API_KEY:
        st.error("⚠️ OpenRouter API key not found. Please add OPENROUTER_API_KEY to your Streamlit secrets.")
        return

    # Model selection
    with st.expander("⚙️ AI Settings", expanded=False):
        selected_model = st.selectbox(
            "Choose AI Model",
            [
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "openai/gpt-4-turbo",
                "openai/gpt-3.5-turbo",
                "google/gemini-pro"
            ],
            index=2
        )

    # File upload section
    with st.expander("📤 Upload Excel File", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose an Excel file", 
            type=["xlsx", "xls"],
            help="Upload your Excel file for processing"
        )

    # AI prompt section
    with st.expander("🧠 AI Instructions", expanded=True):
        prompt = st.text_area(
            "What would you like AI to do with your data?",
            placeholder="e.g., 'Remove empty rows', 'Summarize sales by month', 'Clean inconsistent formatting'...",
            height=150,
            help="Be as specific as possible about what transformations or analysis you want"
        )

    if uploaded_file and prompt:
        try:
            with st.spinner("🔍 Reading and processing your file..."):
                # Read Excel file
                try:
                    df = pd.read_excel(uploaded_file)
                    if df.empty:
                        st.warning("⚠️ The uploaded file is empty.")
                        return
                except Exception as e:
                    st.error(f"❌ Failed to read Excel file: {str(e)}")
                    return

                # Convert to CSV for AI processing
                raw_data = df.to_csv(index=False)

                # Call OpenRouter API
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": selected_model,
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are a helpful data analyst. Respond with clean, well-formatted CSV data that can be directly read by pandas."
                        },
                        {
                            "role": "user",
                            "content": f"Here is the data:\n{raw_data}\n\nInstruction:\n{prompt}\n\nPlease return only the cleaned/processed data in CSV format, with no additional commentary or explanation."
                        }
                    ],
                    "temperature": 0.3
                }

                try:
                    response = requests.post(
                        OPENROUTER_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    response.raise_for_status()
                    ai_reply = response.json()["choices"][0]["message"]["content"]
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ OpenRouter API error: {str(e)}")
                    if response.status_code == 429:
                        st.error("You've exceeded your rate limits. Please try again later or upgrade your plan.")
                    return

                # Process AI response
                try:
                    cleaned_df = pd.read_csv(BytesIO(ai_reply.encode()))
                    
                    st.success("✅ Data processed successfully!")
                    st.balloons()
                    
                    st.subheader("Processed Data Preview")
                    st.dataframe(cleaned_df)
                    
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        cleaned_df.to_excel(writer, index=False)
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Download Processed Excel",
                        data=output.getvalue(),
                        file_name="processed_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                except Exception as e:
                    st.error("⚠️ Could not convert AI response to a data table. Showing raw response:")
                    st.code(ai_reply)
                    st.error(f"Error details: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()