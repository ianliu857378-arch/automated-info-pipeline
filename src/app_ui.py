import streamlit as st
import pandas as pd
import os
import zipfile
import io
import tempfile
import hashlib
import re
import logging
from PIL import Image
from datetime import datetime
from data_cleaner import DataCleaner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 安全配置
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 50
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB per image
ALLOWED_EXCEL_EXTENSIONS = ['.xlsx', '.xls']
ALLOWED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']

# Page Config
st.set_page_config(
    page_title="Automated Info Pipeline",
    page_icon="🚀",
    layout="wide"
)


# 工具函数
def sanitize_filename(filename):
    """清理文件名，防止路径遍历"""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = filename[:100]
    return filename if filename else "unnamed"


def validate_file_magic(file_obj, expected_magic):
    """验证文件魔数"""
    file_obj.seek(0)
    magic = file_obj.read(4)
    file_obj.seek(0)
    return magic[:2] == expected_magic


def save_uploaded_file_secure(uploaded_file, extension):
    """安全地保存上传文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
    safe_filename = f"temp_{timestamp}_{file_hash}{extension}"

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, safe_filename)

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return temp_path


# Title
st.title("🚀 Automated Info-Processing Pipeline")
st.markdown("""
**Automate your tedious operations tasks.**  
This app demonstrates Python's ability to clean data and process images in bulk.
""")

# Sidebar
st.sidebar.header("Configuration")

# 使用secrets或环境变量
api_key = st.secrets.get("GEMINI_API_KEY") if hasattr(st, 'secrets') else None

if not api_key:
    api_key = st.sidebar.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter your Google Gemini API Key",
        help="⚠️ 不会保存，仅本次会话使用"
    )

if not api_key:
    st.sidebar.warning("⚠️ Please provide an API Key to enable AI summarization.")

# Tabs
tab1, tab2 = st.tabs(["📊 Intelligent Data Cleaner", "🖼️ Batch Image Processor"])

# --- TAB 1: DATA CLEANER ---
with tab1:
    st.header("Excel Data Cleaner")
    st.markdown(
        "Upload a raw 'dirty' Excel file to automatically clean formatting, remove duplicates, and generate an AI summary.")

    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help=f"最大文件大小: {MAX_FILE_SIZE / 1024 / 1024}MB"
    )

    if uploaded_file:
        try:
            # 验证文件大小
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error(f"❌ 文件大小超过 {MAX_FILE_SIZE / 1024 / 1024}MB 限制")
                st.stop()

            # 验证文件扩展名
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in ALLOWED_EXCEL_EXTENSIONS:
                st.error("❌ 只支持 Excel 文件 (.xlsx, .xls)")
                st.stop()

            # 验证文件魔数
            if not validate_file_magic(uploaded_file, b'PK'):
                st.error("❌ 文件格式无效")
                st.stop()

            # 安全保存文件
            temp_path = save_uploaded_file_secure(uploaded_file, file_ext)

            # Show Raw Data
            st.subheader("Raw Data Preview")
            df_raw = pd.read_excel(temp_path, nrows=100)  # 限制预览行数
            st.dataframe(df_raw.head(10))

            if st.button("🚀 Start Cleaning Pipeline"):
                with st.spinner("Cleaning data and generating AI insights..."):
                    try:
                        # Initialize Cleaner
                        cleaner = DataCleaner(api_key=api_key if api_key else None)

                        # Run Cleaning
                        df_cleaned, summary = cleaner.clean_excel(temp_path)

                        # Display Results
                        st.success("✅ Cleaning Complete!")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Cleaned Data")
                            st.dataframe(df_cleaned.head(10))
                            st.metric("Rows Removed", len(df_raw) - len(df_cleaned))

                        with col2:
                            st.subheader("🤖 AI Analysis Report")
                            if api_key and summary:
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

                    except pd.errors.ParserError:
                        st.error("❌ Excel 文件格式错误")
                        logger.error("Parser error processing Excel file")
                    except Exception as e:
                        st.error("❌ 处理失败，请检查文件格式")
                        logger.exception(f"Error cleaning Excel: {e}")
                    finally:
                        # 清理内存
                        del df_raw
                        if 'df_cleaned' in locals():
                            del df_cleaned
                        import gc

                        gc.collect()

            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Cleaned up temp file: {temp_path}")

        except Exception as e:
            st.error("❌ 文件处理失败")
            logger.exception(f"Error in data cleaner tab: {e}")

# --- TAB 2: IMAGE PROCESSOR ---
with tab2:
    st.header("Batch Image Processor")
    st.markdown(f"""
    Upload multiple images (PNG/JPG) to batch resize and convert them to standard JPEG format.

    **限制：**
    - 最多 {MAX_FILES} 个文件
    - 每个文件不超过 {MAX_IMAGE_SIZE / 1024 / 1024}MB
    """)

    uploaded_images = st.file_uploader(
        "Upload Images",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )

    if uploaded_images:
        # 验证数量
        if len(uploaded_images) > MAX_FILES:
            st.error(f"❌ 最多只能上传 {MAX_FILES} 个文件")
            st.stop()

        # 验证大小
        for img in uploaded_images:
            if img.size > MAX_IMAGE_SIZE:
                st.error(f"❌ 文件 {img.name} 超过 {MAX_IMAGE_SIZE / 1024 / 1024}MB 限制")
                st.stop()

        if st.button("⚙️ Process Images"):
            with st.spinner(f"Processing {len(uploaded_images)} images..."):
                zip_buffer = io.BytesIO()
                processed_count = 0
                errors = []

                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for img_file in uploaded_images:
                        try:
                            # 打开图片
                            image = Image.open(img_file)

                            # 验证图片
                            if image.size[0] * image.size[1] > 100000000:  # 100MP
                                errors.append(f"{img_file.name}: 图片太大")
                                continue

                            # Convert to RGB
                            if image.mode in ('RGBA', 'P', 'L'):
                                image = image.convert('RGB')

                            # Resize
                            image.thumbnail((600, 800), Image.Resampling.LANCZOS)

                            # Save to Bytes
                            img_byte_arr = io.BytesIO()
                            image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)

                            # 清理文件名
                            safe_name = sanitize_filename(img_file.name)
                            new_filename = os.path.splitext(safe_name)[0] + ".jpg"

                            # Add to Zip
                            zf.writestr(new_filename, img_byte_arr.getvalue())

                            processed_count += 1

                            # 清理内存
                            image.close()

                        except Exception as e:
                            errors.append(f"{img_file.name}: 处理失败")
                            logger.error(f"Error processing {img_file.name}: {e}")

                # 显示结果
                if processed_count > 0:
                    st.success(f"🎉 成功处理 {processed_count} 个图片!")

                    if errors:
                        st.warning(f"⚠️ {len(errors)} 个文件处理失败")
                        with st.expander("查看错误"):
                            for error in errors:
                                st.text(error)

                    # Download Zip
                    st.download_button(
                        label="📦 Download All (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="processed_images.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("❌ 所有图片处理失败")