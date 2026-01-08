import pandas as pd
from google import genai
from google.genai.errors import APIError
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataCleaner:
    def __init__(self, api_key=None, model="gemini-2.0-flash-exp"):
        """Initalize the DataCleaner with Gemini API Client."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
                print("✅ AI Client Initialized.")
            else:
                print("⚠️ Warning: GEMINI_API_KEY not found. AI features will be disabled.")
        except Exception as e:
            print(f"❌ Error initializing AI client: {e}")

    def clean_excel(self, file_path, output_path=None, user_mapping=None):
        """
        Main runner for the data cleaning pipeline.
        Reads Excel -> Cleans Data -> Generates AI Summary -> Saves Output.

        Args:
            file_path: Path to the Excel file
            output_path: Optional output path for cleaned file
            user_mapping: Dictionary mapping original column names to standard fields
                         e.g., {"薪资": "TotalPrice", "年龄": "Age"}
        """
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found at {file_path}")
            return None, "File not found"

        print(f"📂 Reading file: {file_path}")
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            print(f"❌ Error reading Excel: {e}")
            return None, f"Error reading file: {e}"

        # Cleaning Log
        logs = []

        # 1. Drop Empty Rows
        initial_rows = len(df)
        df.dropna(how='all', inplace=True)
        rows_removed = initial_rows - len(df)
        if rows_removed > 0:
            logs.append(f"Removed {rows_removed} completely empty rows.")

        # 2. Apply Column Mapping
        if user_mapping:
            # Use user-provided mapping
            df.rename(columns=user_mapping, inplace=True)
            logs.append(f"Applied user column mapping: {len(user_mapping)} columns mapped.")
            logs.append(f"Mapped fields: {', '.join(user_mapping.values())}")
        else:
            # Fallback to hardcoded mapping for backward compatibility
            column_mapping = {
                'ID': 'SaleID',
                '姓名': 'CustomerName',
                '年龄': 'Age',
                '性别': 'Gender',
                '邮箱': 'Email',
                '注册日期': 'OrderDate',
                '城市': 'City',
                '城市': 'City',
                '消费金额': 'TotalPrice',
                '消费金额': 'TotalPrice',
                '薪资': 'TotalPrice'
            }
            df.rename(columns=column_mapping, inplace=True)
            logs.append("Applied default column mapping (backward compatibility mode).")

        # 3. Post-Mapping Standardization (Critical Fallback)
        # Ensure common columns are mapped even if missed by UI/User mapping
        fallback_mapping = {
            'Wage': 'TotalPrice',
            '薪资': 'TotalPrice',
            'join_date': 'OrderDate'
        }
        
        for source, target in fallback_mapping.items():
            if source in df.columns and target not in df.columns:
                df.rename(columns={source: target}, inplace=True)
                logs.append(f"Auto-mapped leftover column '{source}' to '{target}' for cleaning.")

        # Helper function to check if field exists
        def has_field(field_name):
            return field_name in df.columns
            
        print(f"DEBUG: Current Columns: {df.columns.tolist()}")

        # ========== Conditional Field Processing ==========

        # 3. Clean Numeric/Financial Fields
        numeric_fields = {
            'TotalPrice': '总价/金额',
            'UnitPrice': '单价',
            'Quantity': '数量',
            'Revenue': '收入',
            'Cost': '成本',
            'Rating': '评分',
            'Salary': '薪资'
        }

        for field, label in numeric_fields.items():
            if has_field(field):
                original_count = len(df)
                df[field] = df[field].astype(str).str.replace(r'[$,¥￥,，\s]', '', regex=True)  # Also remove commas (English/Chinese) and spaces
                df[field] = pd.to_numeric(df[field], errors='coerce')

                # For financial fields, replace NaN with 0 instead of dropping rows
                # This preserves data rows even if the value couldn't be converted
                invalid_count = df[field].isna().sum()
                if field in ['TotalPrice', 'UnitPrice', 'Revenue', 'Cost']:
                    if invalid_count > 0:
                        df[field].fillna(0, inplace=True)
                        logs.append(f"Cleaned '{field}' ({label}): Removed symbols and commas, converted to numeric. {invalid_count} invalid values replaced with 0 (rows preserved).")
                    else:
                        logs.append(f"Cleaned '{field}' ({label}): Removed currency symbols and commas, converted to numeric.")
                else:
                    logs.append(f"Cleaned '{field}' ({label}): Converted to numeric format.")

        # 4. Clean Age Field with Filtering
        if has_field('Age'):
            original_count = len(df)
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
            # Only filter out obviously invalid ages (negative or unreasonably high), not all < 18
            # This allows business scenarios that may need younger ages
            invalid_age_count = len(df[(df['Age'] < 0) | (df['Age'] > 150)])
            df = df[(df['Age'] >= 0) & (df['Age'] <= 150)]
            if invalid_age_count > 0:
                logs.append(f"Processed 'Age': Converted to numeric and filtered out {invalid_age_count} records with invalid age (negative or > 150).")
            else:
                logs.append(f"Processed 'Age': Converted to numeric format.")

        # 5. Clean DateTime Fields
        date_fields = ['OrderDate', 'Join_Date']
        for date_field in date_fields:
            if has_field(date_field):
                original_count = len(df)
                
                # Handle relative dates (Yesterday, Today, Tomorrow)
                # Normalize case for checking
                df[date_field] = df[date_field].astype(str)
                
                def parse_relative_date(val):
                    val_lower = str(val).lower().strip()
                    today = datetime.now()
                    if val_lower == 'yesterday':
                        return (today - timedelta(days=1)).strftime('%Y-%m-%d')
                    elif val_lower == 'today':
                        return today.strftime('%Y-%m-%d')
                    elif val_lower == 'tomorrow':
                        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
                    return val

                # Apply relative date parsing BEFORE standard parsing
                from datetime import datetime, timedelta
                df[date_field] = df[date_field].apply(parse_relative_date)

                # Try multiple date formats for better compatibility
                # First, try common formats explicitly
                date_formats = [
                    '%Y-%m-%d',      # 2023-01-01
                    '%Y/%m/%d',      # 2023/02/15
                    '%m-%d-%Y',      # 03-20-2023
                    '%d-%m-%Y',      # 20-03-2023
                    '%Y.%m.%d',      # 2024.05.12
                    '%m/%d/%Y',      # 03/20/2023
                    '%d/%m/%Y',      # 20/03/2023
                ]

                # Try pandas auto-parsing first (most flexible)
                # Use infer_datetime_format for better format inference
                try:
                    # Try with format='mixed' (pandas 2.0+)
                    df[date_field] = pd.to_datetime(df[date_field], errors='coerce', format='mixed')
                except TypeError:
                    # Fallback for older pandas versions
                    df[date_field] = pd.to_datetime(df[date_field], errors='coerce', infer_datetime_format=True)

                # If auto-parsing failed for some rows, try explicit formats
                if df[date_field].isna().any():
                    na_mask = df[date_field].isna()
                    for date_format in date_formats:
                        if not na_mask.any():
                            break
                        try:
                            # Only try to parse rows that are still NaN
                            parsed_dates = pd.to_datetime(
                                df.loc[na_mask, date_field],
                                errors='coerce',
                                format=date_format
                            )
                            # Update only successfully parsed dates
                            df.loc[na_mask, date_field] = parsed_dates
                            na_mask = df[date_field].isna()
                        except (ValueError, TypeError):
                            continue

                # Only drop rows where date is completely invalid (not just unparseable)
                # This is more lenient - we keep rows even if date parsing fails
                # Uncomment the following line if you want strict date validation:
                # df.dropna(subset=['OrderDate'], inplace=True)

                parsed_count = df[date_field].notna().sum()
                if original_count > parsed_count:
                    logs.append(f"Cleaned '{date_field}': Standardized datetime format, {parsed_count}/{original_count} dates successfully parsed. {original_count - parsed_count} dates could not be parsed (kept as NaN).")
                else:
                    logs.append(f"Cleaned '{date_field}': Standardized datetime format, all dates successfully parsed.")

        # 6. Clean Customer Information Fields
        text_fields = {
            'CustomerName': '客户姓名',
            'ProductName': '产品名称'
        }

        for field, label in text_fields.items():
            if has_field(field):
                df[field] = df[field].astype(str).str.strip()
                
                # Filter out invalid names
                if field == 'CustomerName':
                    # List of invalid names/artifacts to remove
                    invalid_names = ['double clean']
                    # Create a case-insensitive regex pattern
                    pattern = '|'.join([re.escape(name) for name in invalid_names])
                    # Replace matches with empty string or NaN (here we use replace to make them empty, which might be cleaner for display, or NaN)
                    # Let's replace with NaN so they can be handled or dropped if needed, or just kept as empty
                    # Based on user request "clean out", usually means treating as invalid.
                    mask = df[field].str.contains(pattern, case=False, na=False)
                    if mask.any():
                        cleaned_count = mask.sum()
                        df.loc[mask, field] = "" # Clear the value
                        logs.append(f"Cleaned '{field}': Removed {cleaned_count} invalid entries (e.g., 'double clean').")

                # Apply title case for names (optional, can be commented out for Chinese names)
                # df[field] = df[field].str.title()
                logs.append(f"Cleaned '{field}' ({label}): Trimmed whitespace.")

        # 7. Clean Location Fields
        location_fields = {
            'Province': '省份',
            'City': '城市',
            'Address': '地址'
        }

        for field, label in location_fields.items():
            if has_field(field):
                df[field] = df[field].astype(str).str.strip()
                logs.append(f"Cleaned '{field}' ({label}): Trimmed whitespace.")

        # 8. Clean Phone Field
        if has_field('Phone'):
            df['Phone'] = df['Phone'].astype(str).str.replace(r'[^\d+\-() ]', '', regex=True).str.strip()
            logs.append(f"Cleaned 'Phone': Removed special characters, kept only digits and common separators.")

        # 9. Clean Email Field
        if has_field('Email'):
            # Fix common email format errors before validation
            original_count = len(df)
            df['Email'] = df['Email'].astype(str).str.strip().str.lower()

            # Fix common typos: replace '#' with '@'
            df['Email'] = df['Email'].str.replace('#', '@', regex=False)

            # Fix other common separators that should be '@'
            df['Email'] = df['Email'].str.replace('＃', '@', regex=False)  # Full-width hash
            df['Email'] = df['Email'].str.replace('＠', '@', regex=False)  # Full-width @

            # Optional: Remove rows with clearly invalid emails after fixing
            # Uncomment the following lines if you want to filter out emails that still don't match the pattern
            # email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            # invalid_before = len(df)
            # df = df[df['Email'].str.match(email_pattern, na=False)]
            # if invalid_before > len(df):
            #     logs.append(f"Removed {invalid_before - len(df)} rows with invalid email addresses after correction attempts.")

            logs.append(f"Cleaned 'Email': Standardized to lowercase, trimmed whitespace, and fixed common format errors (# → @).")

        # 10. Clean Status/Category Fields
        status_fields = {
            'Status': '状态',
            'Type': '类型',
            'Category': '分类',
            'Level': '等级',
            'Gender': '性别',
            'Department': '部门'
        }

        for field, label in status_fields.items():
            if has_field(field):
                df[field] = df[field].astype(str).str.strip()
                logs.append(f"Cleaned '{field}' ({label}): Trimmed whitespace and standardized format.")

        # 11. Clean IsValid Field (Convert to Boolean)
        if has_field('IsValid'):
            df['IsValid'] = df['IsValid'].astype(str).str.lower().isin(['true', '1', 'yes', '是', 'y', 't'])
            logs.append(f"Cleaned 'IsValid': Converted to boolean (True/False).")

        # 12. Clean Text/Notes Fields
        text_note_fields = {
            'Description': '描述',
            'Remarks': '备注',
            'SKU': '商品编码',
            'Model': '型号',
            'ProductCategory': '产品类别'
        }

        for field, label in text_note_fields.items():
            if has_field(field):
                df[field] = df[field].astype(str).str.strip()
                logs.append(f"Cleaned '{field}' ({label}): Trimmed whitespace.")

        # 13. Deduplication (based on available identifier fields)
        dedup_fields = []
        if has_field('SaleID'):
            dedup_fields.append('SaleID')
        if has_field('Email'):
            dedup_fields.append('Email')
        if has_field('Phone') and 'Email' not in dedup_fields:
            dedup_fields.append('Phone')

        if dedup_fields:
            initial_unique = len(df)
            df.drop_duplicates(subset=dedup_fields, keep='first', inplace=True)
            duplicates_removed = initial_unique - len(df)
            if duplicates_removed > 0:
                logs.append(f"Removed {duplicates_removed} duplicate records based on: {', '.join(dedup_fields)}.")

        print("✅ Data Cleaning Complete.")

        # Generate AI Summary
        summary = self.generate_summary(df, logs)
        print("\n🤖 AI Summary Report:")
        print(summary)

        # Save Output
        if output_path:
            df.to_excel(output_path, index=False)
            print(f"\n💾 Cleaned data saved to: {output_path}")

        return df, summary

    def generate_summary(self, df, cleaning_steps):
        """Uses Gemini to generate a human-readable summary of the cleaning process and data insights."""
        if not self.client:
            return "AI Summary Skipped (Client not initialized)."

        stats = df.describe(include='all').to_markdown()
        steps_str = "\n".join([f"- {s}" for s in cleaning_steps])
        sample = df.head(5).to_markdown()

        prompt = f"""
        You are a Data Analyst. Please summarize the following data processing task.
        
        --- Cleaning Steps Taken ---
        {steps_str}

        --- Data Statistics (Cleaned) ---
        {stats}

        --- Sample Data ---
        {sample}

        Please provide:
        1. A brief summary of the dataset quality before and after cleaning.
        2. Key insights from the data (e.g., average values, distributions).
        3. Any anomalies that were removed (based on the steps).
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config={"temperature": 0.2}
            )
            return response.text
        except APIError as e:
            return f"AI Error: {e.message}"
        except Exception as e:
            return f"Error generating summary: {e}"

if __name__ == "__main__":
    # Example Usage
    cleaner = DataCleaner()
    # Replace with your actual file path for testing
    # cleaner.clean_excel("data/raw_data.xlsx", "data/cleaned_data.xlsx")
