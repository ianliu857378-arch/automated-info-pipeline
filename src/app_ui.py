import streamlit as st
import pandas as pd
import os
import zipfile
import io
from PIL import Image
from data_cleaner import DataCleaner

# Page Config
st.set_page_config(
    page_title="Automated Info Pipeline",
    page_icon="🚀",
    layout="wide"
)

# Title
st.title("🚀 Automated Info-Processing Pipeline")
st.markdown("""
**Automate your tedious operations tasks.**  
This app demonstrates Python's ability to clean data and process images in bulk.
""")

# Sidebar
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", placeholder="Enter your Google Gemini API Key")

if not api_key:
    st.sidebar.warning("⚠️ Please provide an API Key to enable AI summarization.")

# Tabs
tab1, tab2 = st.tabs(["📊 Intelligent Data Cleaner", "🖼️ Batch Image Processor"])

# --- TAB 1: DATA CLEANER ---
with tab1:
    st.header("Excel Data Cleaner")
    st.markdown("Upload a raw 'dirty' Excel file to automatically clean formatting, remove duplicates, and generate an AI summary.")
    
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'])
    
    if uploaded_file:
        try:
            # Save uploaded file to temp
            temp_path = "temp_uploaded.xlsx"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Show Raw Data
            st.subheader("Raw Data Preview")
            df_raw = pd.read_excel(temp_path)
            st.dataframe(df_raw.head())

            if st.button("🚀 Start Cleaning Pipeline"):
                with st.spinner("Cleaning data and generating AI insights..."):
                    # Initialize Cleaner
                    cleaner = DataCleaner(api_key=api_key if api_key else None)
                    
                    # Run Cleaning
                    df_cleaned, summary = cleaner.clean_excel(temp_path)
                    
                    # Display Results
                    st.success("✅ Cleaning Complete!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Cleaned Data")
                        st.dataframe(df_cleaned.head())
                        st.metric("Rows Removed", len(df_raw) - len(df_cleaned))
                    
                    with col2:
                        st.subheader("🤖 AI Analysis Report")
                        if api_key:
                            st.info(summary)
                        else:
                            st.warning("AI Summary skipped (No API Key provided).")
                    
                    # Download Button
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_cleaned.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="💾 Download Cleaned Excel",
                        data=output.getvalue(),
                        file_name="cleaned_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            st.error(f"Error processing file: {e}")

# --- TAB 2: IMAGE PROCESSOR ---
with tab2:
    st.header("Batch Image Processor")
    st.markdown("Upload multiple images (PNG/JPG) to batch resize and convert them to standard JPEG format.")
    
    uploaded_images = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)
    
    if uploaded_images and st.button("⚙️ Process Images"):
        with st.spinner(f"Processing {len(uploaded_images)} images..."):
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                processed_count = 0
                for img_file in uploaded_images:
                    try:
                        image = Image.open(img_file)
                        
                        # Convert to RGB
                        if image.mode in ('RGBA', 'P'):
                            image = image.convert('RGB')
                        
                        # Resize (Thumbnail)
                        image.thumbnail((600, 800))
                        
                        # Save to Bytes
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
                        
                        # Add to Zip
                        new_filename = os.path.splitext(img_file.name)[0] + ".jpg"
                        zf.writestr(new_filename, img_byte_arr.getvalue())
                        
                        processed_count += 1
                    except Exception as e:
                        st.error(f"Error processing {img_file.name}: {e}")
            
            st.success(f"🎉 Successfully processed {processed_count} images!")
            
            # Download Zip
            st.download_button(
                label="📦 Download All (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="processed_images.zip",
                mime="application/zip"
            )
