from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json

# Import your existing helper functions
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

app = FastAPI()

# ✅ CORS (allow frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Test route
@app.get("/")
def home():
    return {"message": "DataNova API is running"}

# ✅ Analyze route (UPDATED)
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # 1. Read the CSV
        df = pd.read_csv(file.file)

        # 2. Clean Data (Strip whitespace, remove unnamed columns)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

        # 3. Convert numeric columns where possible
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # 4. Get Basic Stats
        row_count, col_count = df.shape
        columns = df.columns.tolist()

        # 5. Get Top 10 Entries for Preview (Handle NaNs for JSON safety)
        # fillna("") prevents JSON errors when fields are empty
        head = df.head(10).fillna("").to_dict(orient='records')

        # 6. Generate AI Summary (Safe Block)
        # We wrap this in try/except so if AI fails, the rest of the dashboard still loads
        summary = "Summary unavailable."
        try:
            # Pass a small sample to the summarizer to save tokens/time
            summary = summarize_dataset(df.head(10)) 
        except Exception as e:
            print(f"Summarizer Error: {e}")
            summary = "Could not generate AI summary at this time."

        # 7. Return the Structure the Frontend Expects
        return {
            "fileName": file.filename,
            "row_count": row_count,
            "column_count": col_count,
            "columns": columns,
            "summary": summary,
            "head": head
        }

    except Exception as e:
        return {"error": str(e)}

# ✅ Chart route
@app.post("/chart")
async def chart(
    file: UploadFile = File(...),
    column: str = Form(...),
    top_n: int = Form(10)
):
    df = pd.read_csv(file.file)
    # Ensure columns are stripped here too to match analyze
    df.columns = [col.strip() for col in df.columns]
    
    fig = plot_top_column(df, column, top_n=top_n)
    return fig.to_dict()

# ✅ Ask question route
@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...),
    mode: str = Form("Normal")
):
    df = pd.read_csv(file.file)
    df.columns = [col.strip() for col in df.columns]
    
    answer = ask_dataset_question(df, question, mode=mode)
    return {"answer": answer}