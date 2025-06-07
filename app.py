import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="📊 Excel Data Refiner with AI (Llama 3)",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Excel Data Refiner with AI (Llama 3)")
    st.caption("Upload an Excel file and let AI help clean, transform, or analyze your data")

    # DeepInfra configuration
    DEEPINFRA_API_KEY = st.secrets.get("DEEPINFRA_API_KEY", "")
    DEEPINFRA_API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
    MODEL = "meta-llama/Meta-Llama-3-70B-Instruct"  # Free tier eligible
    
    if not DEEPINFRA_API_KEY:
        st.error("⚠️ DeepInfra API key not found. Please add DEEPINFRA_API_KEY to your Streamlit secrets.")
        st.info("Get a free key: https://deepinfra.com")
        return

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

                # Prepare API request
                headers = {
                    "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a professional data analyst. 
                            Return ONLY cleaned/processed data in CSV format. 
                            No explanations, no additional text."""
                        },
                        {
                            "role": "user",
                            "content": f"DATA:\n{raw_data}\n\nTASK:\n{prompt}\n\nOUTPUT:"
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 4000
                }

                # Call DeepInfra API
                try:
                    response = requests.post(
                        DEEPINFRA_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=45
                    )
                    response.raise_for_status()
                    ai_reply = response.json()["choices"][0]["message"]["content"]
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ DeepInfra API error: {str(e)}")
                    if response.status_code == 429:
                        st.error("Free tier limit reached. Try again later or upgrade.")
                    return

                # Process AI response
                try:
                    cleaned_df = pd.read_csv(BytesIO(ai_reply.encode()))
                    
                    st.success("✅ Data processed successfully!")
                    st.balloons()
                    
                    st.subheader("Processed Data Preview")
                    st.dataframe(cleaned_df)
                    
                    # Prepare download
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