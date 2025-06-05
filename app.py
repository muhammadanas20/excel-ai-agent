import streamlit as st
import pandas as pd
import openai
from io import BytesIO
import time

# Configure page
st.set_page_config(
    page_title="📊 Excel Data Refiner with AI",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Excel Data Refiner with AI")
    st.caption("Upload an Excel file and let AI help clean, transform, or analyze your data")

    # Check for API key
    if "openai_api_key" not in st.secrets:
        st.error("⚠️ OpenAI API key not found in secrets. Please add it to your Streamlit secrets.")
        return

    try:
        openai.api_key = st.secrets["openai_api_key"]
    except Exception as e:
        st.error(f"⚠️ Error setting up OpenAI API: {str(e)}")
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
            # Show loading state
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

                # Call OpenAI API
                try:
                    response = openai.chat.completions.create(
                        model="gpt-4o",  # or "gpt-3.5-turbo"
                        messages=[
                            {"role": "system", "content": "You are a helpful data analyst. Respond with clean, well-formatted CSV data that can be directly read by pandas."},
                            {"role": "user", "content": f"Here is the data:\n{raw_data}\n\nInstruction:\n{prompt}\n\nPlease return only the cleaned/processed data in CSV format, with no additional commentary or explanation."}
                        ],
                        temperature=0.3  # More deterministic output
                    )
                    ai_reply = response.choices[0].message.content
                except Exception as e:
                    st.error(f"❌ OpenAI API error: {str(e)}")
                    return

                # Process AI response
                try:
                    # Parse AI's cleaned data as CSV
                    cleaned_df = pd.read_csv(BytesIO(ai_reply.encode()))
                    
                    st.success("✅ Data processed successfully!")
                    st.balloons()
                    
                    # Display results
                    st.subheader("Processed Data Preview")
                    st.dataframe(cleaned_df)
                    
                    # Create Excel file for download
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        cleaned_df.to_excel(writer, index=False)
                    output.seek(0)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Processed Excel",
                        data=output.getvalue(),
                        file_name="processed_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download the processed data as an Excel file"
                    )
                    
                except Exception as e:
                    st.error("⚠️ Could not convert AI response to a data table. Showing raw response:")
                    st.code(ai_reply)
                    st.error(f"Error details: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()