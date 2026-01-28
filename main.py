from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "DataNova API is running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    df.columns = [col.strip() for col in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

    summary = summarize_dataset(df.head(7))

    return {
        "summary": summary,
        "columns": df.columns.tolist()
    }
