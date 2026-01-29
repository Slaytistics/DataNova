import requests
import pandas as pd
import os
import io
from fastapi import APIRouter, UploadFile, File, Form

router = APIRouter()

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"


# ---------------- SUMMARY ENDPOINT ---------------- #

@router.post("/summary")
async def summarize_dataset(
    file: UploadFile = File(...),
    style: str = Form("Executive Summary")
):
    try:
        df = pd.read_csv(io.BytesIO(await file.read()))
        df.columns = df.columns.str.strip()

        # Store original counts before sampling
        original_row_count = len(df)
        original_column_count = len(df.columns)
        
        # Get column names and head data BEFORE sampling
        columns = df.columns.tolist()
        head_data = df.head(10).to_dict(orient='records')

        # limit dataset for speed (for AI summary only)
        if len(df) > 5000:
            df_sample = df.sample(5000)
        else:
            df_sample = df

        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            summary_text = create_fallback_summary(df)
            mode = "fallback"
        else:
            style_prompts = {
                "Executive Summary": "Give a high-level overview of the dataset for executives.",
                "Technical Analysis": "Provide technical insights about distributions and data quality.",
                "Business Insights": "Extract 2-3 actionable business trends."
            }

            instruction = style_prompts.get(style, style_prompts["Executive Summary"])

            sample_data = df_sample.head(5).to_string(index=False)
            stats = df_sample.describe().round(2).to_string()

            prompt = f"""
You are a professional data analyst.

Task: {instruction}

Columns: {', '.join(df_sample.columns)}

Sample Data:
{sample_data}

Statistics:
{stats}

Rules:
- Use bullet points
- Max 200 words
- Focus only on this dataset
"""

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "You are DataNova AI, a dataset analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.4
            }

            try:
                response = requests.post(
                    TOGETHER_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=12
                )

                if response.status_code == 200:
                    data = response.json()
                    summary_text = data["choices"][0]["message"]["content"]
                    mode = "ai"
                else:
                    summary_text = create_fallback_summary(df)
                    mode = "fallback"
            except Exception as api_error:
                print(f"AI API Error: {api_error}")
                summary_text = create_fallback_summary(df)
                mode = "fallback"

        # Return complete response with all required fields
        return {
            "fileName": file.filename,
            "row_count": original_row_count,
            "column_count": original_column_count,
            "columns": columns,
            "head": head_data,
            "summary": summary_text,
            "mode": mode
        }

    except Exception as e:
        print(f"Error in summarize_dataset: {e}")
        return {"error": str(e)}


# ---------------- FALLBACK SUMMARY ---------------- #

def create_fallback_summary(df: pd.DataFrame) -> str:
    rows, cols = df.shape
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    summary = f"""
**Dataset Overview**
- Total Rows: {rows}
- Total Columns: {cols}

**Column Types**
- Numeric Columns ({len(num_cols)}): {', '.join(num_cols[:5])}
- Categorical Columns ({len(cat_cols)}): {', '.join(cat_cols[:5])}

**Data Quality**
- Missing Values Detected: {df.isnull().sum().sum()}

This summary was generated using statistical analysis (AI service unavailable).
"""
    return summary.strip()