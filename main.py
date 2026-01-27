from fastapi import FastAPI, UploadFile, File
import pandas as pd
from summarizer import summarize_data
from visualizer import generate_visuals

app = FastAPI()

@app.get("/")
def home():
    return {"message": "DataNova API is running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    summary = summarize_data(df)
    visuals = generate_visuals(df)

    return {
        "summary": summary,
        "visuals": visuals
    }
