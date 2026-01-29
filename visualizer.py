import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd

router = APIRouter()

# ---------------- UTILS ---------------- #

def get_columns(df):
    return {
        "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
        "all_columns": df.columns.tolist()
    }


# ---------------- API ---------------- #

@router.post("/visualize")
async def visualize(
    file: UploadFile = File(...),
    chart_type: str = Form(...),   # bar, line, scatter, hist
    x_axis: str = Form(...),
    y_axis: str = Form(None),
    limit: int = Form(50)          # number of rows user wants
):
    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip()

        # limit rows for performance
        df = df.head(limit)

        columns_info = get_columns(df)

        # validate x_axis
        if x_axis not in df.columns:
            return {"error": f"Invalid X axis column: {x_axis}"}

        # validate y_axis if needed
        if chart_type != "hist" and y_axis not in df.columns:
            return {"error": f"Invalid Y axis column: {y_axis}"}

        sns.set_theme(style="darkgrid")
        plt.figure(figsize=(8,5))

        # -------- CHART LOGIC -------- #
        if chart_type == "bar":
            sns.barplot(data=df, x=x_axis, y=y_axis)

        elif chart_type == "line":
            sns.lineplot(data=df, x=x_axis, y=y_axis, marker="o")

        elif chart_type == "scatter":
            sns.scatterplot(data=df, x=x_axis, y=y_axis)

        elif chart_type == "hist":
            sns.histplot(df[x_axis], bins=20)

        else:
            return {"error": "Invalid chart type. Use bar, line, scatter, hist."}

        plt.title(f"{chart_type.capitalize()} Chart")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # -------- IMAGE ENCODE -------- #
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()

        return {
            "chart": img_base64,
            "columns": columns_info,
            "used": {
                "chart_type": chart_type,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "limit": limit
            }
        }

    except Exception as e:
        plt.close()
        return {"error": str(e)}
