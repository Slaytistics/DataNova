import matplotlib
# CRITICAL: Use 'Agg' backend for headless server environments like Render
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd

router = APIRouter()

def get_chart_suggestions(df):
    """Analyzes the dataframe to suggest optimal charts for the AI Assistant."""
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    suggestions = []
    if cat_cols and num_cols:
        suggestions.append(f"A Bar Chart comparing {cat_cols[0]} against {num_cols[0]}.")
    if len(num_cols) >= 2:
        suggestions.append(f"A Scatter Plot showing the relationship between {num_cols[0]} and {num_cols[1]}.")
    
    return suggestions

@router.post("/visualize")
async def visualize(
    file: UploadFile = File(...), 
    chart_type: str = Form("bar"),
    x_axis: str = Form(None),
    y_axis: str = Form(None)
):
    try:
        # 1. Load and Clean Data
        df = pd.read_csv(file.file)
        df.columns = [col.strip() for col in df.columns]

        # 2. Smart Axis Selection
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()

        if not numeric_cols:
            return {"error": "No numeric data found to plot."}

        # Determine axes: User choice -> Detected categorical/numeric -> Default first columns
        final_x = x_axis if x_axis in df.columns else (cat_cols[0] if cat_cols else df.columns[0])
        final_y = y_axis if y_axis in df.columns else numeric_cols[0]

        # 3. Global Styling (DataNova Branding)
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="darkgrid") # Matches your dark theme app
        color_palette = "Oranges_r" 

        # 4. Chart Logic
        if chart_type == "bar":
            sns.barplot(data=df.head(15), x=final_x, y=final_y, palette=color_palette)
        elif chart_type == "line":
            sns.lineplot(data=df, x=final_x, y=final_y, color="#f97316", marker="o")
        elif chart_type == "scatter":
            sns.scatterplot(data=df, x=final_x, y=final_y, color="#ea580c", s=100)
        elif chart_type == "heatmap":
            sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="Oranges")
        elif chart_type == "pie":
            data_pie = df.groupby(final_x)[final_y].sum().head(5)
            plt.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%', colors=sns.color_palette(color_palette))

        plt.title(f"{chart_type.capitalize()} Analysis: {final_y} by {final_x}", fontsize=14, fontweight='bold', color='white')
        plt.xticks(rotation=45, color='white')
        plt.yticks(color='white')
        plt.tight_layout(pad=3.0)

        # 5. Buffer and Base64 Encoding
        buf = io.BytesIO()
        # Save with transparent background to blend into the UI
        plt.savefig(buf, format="png", dpi=150, transparent=True)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close('all') # Essential to clear memory

        return {
            "chart_base64": img_str,
            "analysis_note": f"Visualizing {final_y} trends across {final_x}.",
            "suggestions": get_chart_suggestions(df)
        }

    except Exception as e:
        plt.close('all')
        return {"error": str(e)}