import streamlit as st
import pandas as pd
import os
import zipfile
import io
import tempfile
import hashlib
import re
import logging
import sys
from pathlib import Path
from PIL import Image
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data_cleaner import DataCleaner
from src.image_processor import ImageProcessor

# ========== Configuration & Setup ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 50
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB per image
ALLOWED_EXCEL_EXTENSIONS = ['.xlsx', '.xls']

st.set_page_config(
    page_title="Automated Info Pipeline",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Automated Info Pipeline v2.0.0"
    }
)

# ========== Premium Design System ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Reset & Typography */
    .stApp {
        background-color: #f8fafc; /* Slate 50 */
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1e293b; /* Slate 800 */
    }

    /* Header Styling */
    .hero-section {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
        text-align: center;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white !important;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Card Styling */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #64748b;
        font-weight: 500;
        padding: 0 24px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #eff6ff; /* Blue 50 */
        color: #2563eb; /* Blue 600 */
        font-weight: 600;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(to right, #3b82f6, #2563eb);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.2s;
        width: 100%;
    }

    .stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    /* File Uploader */
    .stFileUploader section {
        background-color: white;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
    }

    /* Metrics & Stats */
    .stat-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .stat-chip {
        background-color: #f0fdf4; /* Green 50 */
        color: #166534; /* Green 800 */
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border: 1px solid #bbf7d0;
    }

    .stat-chip.blue {
        background-color: #eff6ff;
        color: #1e40af;
        border-color: #bfdbfe;
    }
</style>
""", unsafe_allow_html=True)


# ========== Utility Functions ==========
def sanitize_filename(filename):
    """Clean filename to prevent path traversal"""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = filename[:100]
    return filename if filename else "unnamed"


def validate_file_magic(file_obj, expected_magic):
    """Validate file magic numbers"""
    file_obj.seek(0)
    magic = file_obj.read(4)
    file_obj.seek(0)
    if not magic:
        return False
    return magic.startswith(expected_magic)


def save_uploaded_file_secure(uploaded_file, extension):
    """Securely save uploaded file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
    safe_filename = f"temp_{timestamp}_{file_hash}{extension}"
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, safe_filename)

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path


def get_api_key_safely():
    """Safely retrieve API key from secrets or return None"""
    try:
        # Try to access secrets - will raise error if file doesn't exist
        return st.secrets.get("GEMINI_API_KEY", None)
    except (FileNotFoundError, KeyError, AttributeError):
        # Secrets file doesn't exist or key not found
        return None


# ========== Main Application ==========
def main():
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Safe API key retrieval
        api_key = get_api_key_safely()

        if not api_key:
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="Required for AI insights",
                help="Your API key is used only for this session and not stored."
            )
            if not api_key:
                st.warning("⚠️ API Key required for Data Cleaner AI summary.")
        else:
            st.success("✅ API Key connected")

        st.markdown("---")
        st.markdown("### About")
        st.info(
            "**Automated Info Pipeline**\n\n"
            "An AI-powered suite for automating data cleaning and image processing tasks.\n\n"
            "Build v2.0.1"
        )

    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">Automated Info Pipeline</h1>
            <p class="hero-subtitle">Streamline your operations with intelligent data processing and automated batch workflows.</p>
        </div>
    """, unsafe_allow_html=True)

    # Main Tabs
    tab1, tab2 = st.tabs(["📊 Intelligent Data Cleaner", "🖼️ Batch Image Processor"])

    # ========== Tab 1: Data Cleaner ==========
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Clean & Standardize Data")
            st.markdown(
                "Upload 'dirty' Excel files to automatically fix headers, formats, and remove duplicates. Includes AI-powered insights.")
        with col2:
            st.markdown("""
                <div class="stat-container" style="justify-content: flex-end;">
                    <span class="stat-chip">⚡ 80% Time Saved</span>
                    <span class="stat-chip blue">🤖 Gemini AI Powered</span>
                </div>
            """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            key="data_cleaner_up",
            help=f"Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

        if uploaded_file:
            try:
                # Validation
                if uploaded_file.size > MAX_FILE_SIZE:
                    st.error(f"❌ File too large. Limit is {MAX_FILE_SIZE / 1024 / 1024}MB")
                    st.stop()

                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                temp_path = save_uploaded_file_secure(uploaded_file, file_ext)

                # Preview
                st.markdown("#### Raw Data Preview")
                df_raw = pd.read_excel(temp_path, nrows=5)
                st.dataframe(df_raw, use_container_width=True)

                if st.button("🚀 Start Cleaning Pipeline", key="clean_btn"):
                    with st.spinner("Analyzing and cleaning data... this may take a moment"):
                        try:
                            cleaner = DataCleaner(api_key=api_key if api_key else None)
                            df_cleaned, summary = cleaner.clean_excel(temp_path)

                            st.success("✅ Cleaning Complete!")

                            # Results Section
                            r_col1, r_col2 = st.columns(2)
                            with r_col1:
                                st.markdown("#### Cleaned Data Preview")
                                st.dataframe(df_cleaned.head(), use_container_width=True)
                                st.metric("Rows optimized", f"{len(df_raw)} → {len(df_cleaned)}")

                            with r_col2:
                                st.markdown("#### 🤖 AI Analysis")
                                if api_key and summary:
                                    st.info(summary)
                                else:
                                    st.warning("AI Summary skipped (No API Key).")

                            # Download
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df_cleaned.to_excel(writer, index=False)

                            st.download_button(
                                label="📥 Download Cleaned Excel",
                                data=output.getvalue(),
                                file_name=f"cleaned_{sanitize_filename(uploaded_file.name)}",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                        except Exception as e:
                            st.error(f"Processing failed: {str(e)}")
                            logger.error(f"Cleaning error: {e}")

            except Exception as e:
                st.error(f"Error loading file: {e}")
            finally:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)

    # ========== Tab 2: Image Processor ==========
    with tab2:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Batch Image Processing")
            st.markdown(
                "Resize, format, and optimize multiple images at once. Perfect for ID card systems or gallery uploads.")
        with col2:
            st.markdown("""
                <div class="stat-container" style="justify-content: flex-end;">
                    <span class="stat-chip blue">🚀 20x Faster</span>
                </div>
            """, unsafe_allow_html=True)

        uploaded_images = st.file_uploader(
            "Upload Images (PNG, JPG, JPEG)",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="img_up"
        )

        if uploaded_images:
            if len(uploaded_images) > MAX_FILES:
                st.error(f"❌ Max {MAX_FILES} files allowed.")
                st.stop()

            st.info(f"📸 {len(uploaded_images)} images queued")

            # Settings
            with st.expander("⚙️ Output Settings", expanded=True):
                sc1, sc2 = st.columns(2)
                with sc1:
                    t_width = st.number_input("Target Width (px)", value=600, min_value=100)
                with sc2:
                    t_height = st.number_input("Target Height (px)", value=800, min_value=100)

            if st.button("⚡ Process All Images", key="img_proc_btn"):
                with st.spinner(f"Processing {len(uploaded_images)} images..."):
                    zip_buffer = io.BytesIO()
                    success_count = 0
                    errors = []

                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        for img_file in uploaded_images:
                            try:
                                if img_file.size > MAX_IMAGE_SIZE:
                                    errors.append(f"{img_file.name}: Exceeds 5MB")
                                    continue

                                image = Image.open(img_file)
                                if image.mode in ('RGBA', 'P', 'L'):
                                    image = image.convert('RGB')

                                image.thumbnail((t_width, t_height), Image.Resampling.LANCZOS)

                                img_byte = io.BytesIO()
                                image.save(img_byte, format='JPEG', quality=85, optimize=True)

                                safe_name = sanitize_filename(img_file.name)
                                new_name = os.path.splitext(safe_name)[0] + ".jpg"
                                zf.writestr(new_name, img_byte.getvalue())
                                success_count += 1

                            except Exception as e:
                                errors.append(f"{img_file.name}: {str(e)}")

                    if success_count > 0:
                        st.success(f"🎉 Successfully processed {success_count} images!")
                        if errors:
                            st.warning(f"⚠️ {len(errors)} files failed.")
                            for err in errors:
                                st.write(err)

                        st.download_button(
                            label="📦 Download Batch (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="processed_images.zip",
                            mime="application/zip"
                        )
                    else:
                        st.error("❌ No images were successfully processed.")


if __name__ == "__main__":
    main()