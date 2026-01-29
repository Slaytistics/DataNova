import requests
import os
import pandas as pd
import io
from fastapi import APIRouter, UploadFile, File, Form

router = APIRouter()

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"


# ---------------- CHAT ENDPOINT ---------------- #

@router.post("/chat")
async def ask_dataset_question(
    file: UploadFile = File(...),
    question: str = Form(...),
    mode: str = Form("Normal")
):
    try:
        df = pd.read_csv(io.BytesIO(await file.read()))
        df.columns = df.columns.str.strip()

        # limit rows for speed & token safety
        if len(df) > 3000:
            df = df.sample(3000)

        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            return {"answer": create_fallback_answer(df, question), "mode": "fallback"}

        context = prepare_dataset_context(df)

        prompt = f"""
You are DataNova AI. You MUST answer strictly using the dataset below.

Dataset Context:
{context}

User Question: {question}

Rules:
- Do not invent information
- Answer only from the dataset
- If answer is not in data, say "Not found in the dataset"
- Keep response under 150 words
"""

        max_tokens, temperature = get_mode_parameters(mode)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are a dataset question-answering assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = requests.post(
            TOGETHER_API_URL,
            headers=headers,
            json=payload,
            timeout=12
        )

        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return {"answer": answer, "mode": "ai"}
        else:
            return {"answer": create_fallback_answer(df, question), "mode": "fallback"}

    except Exception as e:
        return {"error": str(e)}


# ---------------- CONTEXT BUILDER ---------------- #

def prepare_dataset_context(df: pd.DataFrame) -> str:
    rows = len(df)
    cols = df.columns.tolist()

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    context = f"""
OVERVIEW:
Rows: {rows}
Columns: {', '.join(cols)}

NUMERIC COLUMNS: {', '.join(numeric_cols[:5])}
CATEGORICAL COLUMNS: {', '.join(cat_cols[:5])}

SAMPLE DATA:
{df.head(5).to_string(index=False)}
"""
    return context.strip()


# ---------------- MODE PARAMETERS ---------------- #

def get_mode_parameters(mode: str):
    if mode == "Deep":
        return 500, 0.3   # accurate
    elif mode == "Quick":
        return 200, 0.7   # faster
    else:
        return 350, 0.5   # balanced


# ---------------- FALLBACK ANSWERS ---------------- #

def create_fallback_answer(df: pd.DataFrame, question: str) -> str:
    q = question.lower()

    if "how many rows" in q or "row count" in q:
        return f"The dataset contains {len(df)} rows."

    if "columns" in q or "column names" in q:
        return f"The dataset columns are: {', '.join(df.columns.tolist())}."

    if "missing" in q or "null" in q:
        return f"There are {df.isnull().sum().sum()} missing values in the dataset."

    if "average" in q or "mean" in q:
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if num_cols:
            return f"The average of {num_cols[0]} is {df[num_cols[0]].mean():.2f}"

    return (
        "I couldn't find that information in the dataset. "
        "Try asking about row count, column names, missing values, or averages."
    )
