from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# 1️⃣ Create app
app = FastAPI()

# 2️⃣ Add CORS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow frontend from Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3️⃣ Test route
@app.get("/")
def home():
    return {"message": "DataNova API is running"}

# 4️⃣ Analyze route
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    df.columns = [col.strip() for col in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    summary = summarize_dataset(df.head(7))

    return {
        "summary": summary,
        "columns": df.columns.tolist()
    }

# 5️⃣ Chart route
@app.post("/chart")
async def chart(
    file: UploadFile = File(...),
    column: str = Form(...),
    top_n: int = Form(10)
):
    df = pd.read_csv(file.file)
    fig = plot_top_column(df, column, top_n=top_n)
    return fig.to_dict()

# 6️⃣ Ask question route
@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...),
    mode: str = Form("Normal")
):
    df = pd.read_csv(file.file)
    answer = ask_dataset_question(df, question, mode=mode)
    return {"answer": answer}
