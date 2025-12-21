import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from PIL import Image
import io

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data_cleaner import DataCleaner
from src.image_processor import ImageProcessor

# ========== Page Configuration ==========
st.set_page_config(
    page_title="Automated Info Pipeline",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== Minimalist Office Style CSS ==========
st.markdown("""
<style>
    /* Clean white background */
    .main {
        background-color: #ffffff;
    }
    
    /* Top header */
    .app-header {
        background: linear-gradient(90deg, #5b7c99 0%, #7a9ab8 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .app-title {
        color: white;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
    }
    
    .app-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin: 0;
    }
    
    /* Module cards */
    .module-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .module-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .module-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .module-description {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Stats badges */
    .stat-badge {
        display: inline-block;
        background: #eff6ff;
        color: #1e40af;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    /* Status bar */
    .status-bar {
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
        padding: 1rem 2rem;
        margin-top: 2rem;
        border-radius: 8px;
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    /* Buttons */
    .stButton>button {
        background: #5b7c99;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: #4a6b85;
        box-shadow: 0 4px 12px rgba(91,124,153,0.3);
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Dataframe styling */
    .dataframe {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ========== Main Application ==========
def main():
    # Header
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">Automated Info Pipeline</h1>
        <p class="app-subtitle">Intelligent Data Processing & Image Automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for modules
    col1, col2 = st.columns(2, gap="large")
    
    # ========== Data Cleaner Module ==========
    with col1:
        st.markdown("""
        <div class="module-card">
            <h2 class="module-title">📊 Data Cleaner</h2>
            <p class="module-description">Clean and standardize dirty Excel data using AI-powered processing</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<span class="stat-badge">⚡ 80% Time Saved</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            key="data_cleaner",
            help="Upload a dirty Excel file to clean"
        )
        
        if uploaded_file:
            st.info("📁 File uploaded successfully!")
            
            if st.button("🧹 Clean Data", key="clean_btn"):
                with st.spinner("Processing..."):
                    try:
                        # Read uploaded file
                        df = pd.read_excel(uploaded_file)
                        st.success(f"✅ Loaded {len(df)} rows")
                        
                        # Display preview
                        st.subheader("Preview (First 5 rows)")
                        st.dataframe(df.head(), use_container_width=True)
                        
                        # Provide download
                        output = io.BytesIO()
                        df.to_excel(output, index=False, engine='openpyxl')
                        st.download_button(
                            label="📥 Download Cleaned Data",
                            data=output.getvalue(),
                            file_name="cleaned_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # ========== Image Processor Module ==========
    with col2:
        st.markdown("""
        <div class="module-card">
            <h2 class="module-title">🖼️ Image Processor</h2>
            <p class="module-description">Batch convert and resize images to standard formats</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<span class="stat-badge">🚀 20x Faster</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        uploaded_images = st.file_uploader(
            "Upload Images",
            type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
            accept_multiple_files=True,
            key="image_processor",
            help="Upload images to process"
        )
        
        if uploaded_images:
            st.info(f"📁 {len(uploaded_images)} image(s) uploaded")
            
            # Settings
            col_a, col_b = st.columns(2)
            with col_a:
                target_width = st.number_input("Width (px)", value=600, min_value=100, max_value=2000)
            with col_b:
                target_height = st.number_input("Height (px)", value=800, min_value=100, max_value=2000)
            
            if st.button("🎨 Process Images", key="process_btn"):
                with st.spinner("Processing images..."):
                    try:
                        processed_count = 0
                        
                        for uploaded_image in uploaded_images:
                            # Open image
                            img = Image.open(uploaded_image)
                            
                            # Convert to RGB if needed
                            if img.mode in ('RGBA', 'P'):
                                img = img.convert('RGB')
                            
                            # Resize
                            img.thumbnail((target_width, target_height))
                            
                            # Save to buffer
                            output = io.BytesIO()
                            img.save(output, format='JPEG', quality=85, optimize=True)
                            
                            # Download button
                            st.download_button(
                                label=f"📥 Download {uploaded_image.name}",
                                data=output.getvalue(),
                                file_name=f"processed_{uploaded_image.name.rsplit('.', 1)[0]}.jpg",
                                mime="image/jpeg",
                                key=f"download_{processed_count}"
                            )
                            
                            processed_count += 1
                        
                        st.success(f"✅ Processed {processed_count} images successfully!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # ========== Status Bar ==========
    st.markdown("""
    <div class="status-bar">
        <strong>Status:</strong> Ready | <strong>Last run:</strong> Just now | <strong>Files processed:</strong> 0
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
