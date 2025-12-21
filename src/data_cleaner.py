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

    def clean_excel(self, file_path, output_path=None):
        """
        Main runner for the data cleaning pipeline.
        Reads Excel -> Cleans Data -> Generates AI Summary -> Saves Output.
        """
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found at {file_path}")
            return

        print(f"📂 Reading file: {file_path}")
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            print(f"❌ Error reading Excel: {e}")
            return

        # Cleaning Log
        logs = []

        # 1. Drop Empty Rows
        initial_rows = len(df)
        df.dropna(how='all', inplace=True)
        logs.append(f"Removed {initial_rows - len(df)} completely empty rows.")

        # 2. Standardize Column Names
        # Mapping expected Chinese headers to English standard keys
        column_mapping = {
            'ID': 'SaleID',
            '姓名': 'CustomerName',
            '年龄': 'Age',
            '性别': 'Gender',
            '邮箱': 'CustomerEmail',
            '注册日期': 'OrderDate',
            '城市': 'Region',
            '消费金额': 'TotalPrice'
        }
        df.rename(columns=column_mapping, inplace=True)
        logs.append("Standardized column names (mapped CN to EN).")

        # 3. Clean 'TotalPrice' (Remove currency symbols, convert to float)
        if 'TotalPrice' in df.columns:
            df['TotalPrice'] = df['TotalPrice'].astype(str).str.replace(r'[$,¥]', '', regex=True)
            df['TotalPrice'] = pd.to_numeric(df['TotalPrice'], errors='coerce')
            df.dropna(subset=['TotalPrice'], inplace=True)
            logs.append("Cleaned 'TotalPrice': Removed symbols and converted to numeric.")

        # 4. Clean 'OrderDate'
        if 'OrderDate' in df.columns:
            df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
            df.dropna(subset=['OrderDate'], inplace=True)
            logs.append("Cleaned 'OrderDate': Standardized datetime format.")

        # 5. Clean 'Region' (Title case)
        if 'Region' in df.columns:
            df['Region'] = df['Region'].astype(str).str.title().str.strip()
            logs.append("Cleaned 'Region': Applied title case and trimmed whitespace.")

        # 6. Filter Invalid Age
        if 'Age' in df.columns:
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
            df = df[df['Age'] >= 18]
            logs.append("Filtered data: Excluded records with Age < 18 or invalid age.")

        # Deduplicate
        if 'SaleID' in df.columns and 'CustomerEmail' in df.columns:
            initial_unique = len(df)
            df.drop_duplicates(subset=['SaleID', 'CustomerEmail'], keep='first', inplace=True)
            logs.append(f"Removed {initial_unique - len(df)} duplicate records.")

        print("✅ Data Cleaning Complete.")
        
        # Generare AI Summary
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
