import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd

router = APIRouter()

@router.post("/visualize")
async def visualize(file: UploadFile = File(...), chart_type: str = Form("bar")):
    df = pd.read_csv(file.file)
    
    # Auto-select numeric columns for plotting
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return {"error": "No numeric data found to plot"}

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    # Simple logic to pick columns
    x = df.columns[0] # Usually a label/name
    y = numeric_cols[0]

    if chart_type == "bar":
        sns.barplot(data=df.head(10), x=x, y=y, palette="Oranges")
    elif chart_type == "line":
        sns.lineplot(data=df, x=x, y=y, color="#f97316")
    elif chart_type == "heatmap":
        sns.heatmap(df.corr(), annot=True, cmap="Oranges")
    elif chart_type == "scatter":
        sns.scatterplot(data=df, x=df.columns[1], y=y, hue=x)
    
    plt.title(f"{chart_type.capitalize()} Analysis of {file.filename}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    
    # Encode to Base64
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    return {"chart_base64": img_str}