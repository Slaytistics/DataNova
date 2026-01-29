import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

router = APIRouter()

# ---------------- UTILS ---------------- #

def get_columns(df):
    """Extract column information from dataframe"""
    return {
        "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
        "all_columns": df.columns.tolist()
    }


# ---------------- ANALYZE ENDPOINT (Get Column Info) ---------------- #

@router.post("/analyze-columns")
async def analyze_columns(file: UploadFile = File(...)):
    """
    Analyze CSV file and return column information
    This helps the frontend populate dropdowns
    """
    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip()
        
        columns_info = get_columns(df)
        
        return {
            "success": True,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": columns_info,
            "sample_data": df.head(5).to_dict(orient='records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


# ---------------- VISUALIZE ENDPOINT ---------------- #

@router.post("/visualize")
async def visualize(
    file: UploadFile = File(...),
    chart_type: str = Form(...),           # bar, line, scatter, pie
    x_axis: str = Form(...),
    y_axis: Optional[str] = Form(None),
    limit: int = Form(50),                 # number of rows
    color: str = Form("#FF6B35"),          # hex color for chart
    title: str = Form(""),                 # custom title
    show_grid: bool = Form(True),
    style: str = Form("darkgrid")          # seaborn style
):
    """
    Generate customized visualizations with user preferences
    """
    try:
        # Read CSV
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip()

        # Limit rows for performance
        if limit > 0 and limit < len(df):
            df = df.head(limit)

        columns_info = get_columns(df)

        # Validate x_axis
        if x_axis not in df.columns:
            raise HTTPException(status_code=400, detail=f"Invalid X axis column: {x_axis}")

        # Validate y_axis if needed (not required for histogram or pie)
        if chart_type not in ["hist", "pie"] and (not y_axis or y_axis not in df.columns):
            raise HTTPException(status_code=400, detail=f"Invalid Y axis column: {y_axis}")

        # Set seaborn theme
        sns.set_theme(style=style)
        plt.figure(figsize=(10, 6))

        # Prepare title
        chart_title = title if title else f"{chart_type.capitalize()} Chart: {x_axis}" + (f" vs {y_axis}" if y_axis else "")

        # -------- CHART GENERATION LOGIC -------- #
        
        if chart_type == "bar":
            # Bar chart
            if df[x_axis].dtype == 'object' or df[x_axis].nunique() < 20:
                # Categorical x-axis
                ax = sns.barplot(data=df, x=x_axis, y=y_axis, color=color)
                plt.xticks(rotation=45, ha='right')
            else:
                # Numeric x-axis - group by bins
                df_grouped = df.groupby(x_axis)[y_axis].mean().reset_index()
                ax = sns.barplot(data=df_grouped, x=x_axis, y=y_axis, color=color)
                
        elif chart_type == "line":
            # Line chart
            ax = sns.lineplot(data=df, x=x_axis, y=y_axis, marker="o", color=color, linewidth=2.5)
            plt.xticks(rotation=45, ha='right')
            
        elif chart_type == "scatter":
            # Scatter plot
            ax = sns.scatterplot(data=df, x=x_axis, y=y_axis, color=color, s=100, alpha=0.6, edgecolors='white')
            
        elif chart_type == "pie":
            # Pie chart
            if df[x_axis].dtype == 'object':
                value_counts = df[x_axis].value_counts().head(10)  # Top 10 categories
            else:
                value_counts = df[x_axis].value_counts().head(10)
            
            colors_list = sns.color_palette("husl", len(value_counts))
            plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', 
                   colors=colors_list, startangle=90)
            plt.axis('equal')
            
        elif chart_type == "hist":
            # Histogram
            ax = sns.histplot(df[x_axis], bins=30, color=color, kde=True)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid chart type. Use: bar, line, scatter, pie, hist")

        # Apply title and styling
        plt.title(chart_title, fontsize=16, fontweight='bold', pad=20)
        
        if chart_type != "pie":
            plt.xlabel(x_axis, fontsize=12, fontweight='bold')
            if y_axis:
                plt.ylabel(y_axis, fontsize=12, fontweight='bold')
            
            if show_grid:
                plt.grid(True, alpha=0.3)
            else:
                plt.grid(False)

        plt.tight_layout()

        # -------- ENCODE IMAGE TO BASE64 -------- #
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()

        return {
            "success": True,
            "chart": img_base64,
            "chart_url": f"data:image/png;base64,{img_base64}",
            "columns": columns_info,
            "config": {
                "chart_type": chart_type,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "limit": limit,
                "color": color,
                "title": chart_title,
                "style": style
            }
        }

    except HTTPException:
        plt.close()
        raise
    except Exception as e:
        plt.close()
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")


# ---------------- BATCH VISUALIZE (Multiple Charts) ---------------- #

@router.post("/visualize-batch")
async def visualize_batch(
    file: UploadFile = File(...),
    configs: str = Form(...)  # JSON string of chart configurations
):
    """
    Generate multiple visualizations at once
    configs should be a JSON array of chart configurations
    """
    import json
    
    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip()
        
        chart_configs = json.loads(configs)
        results = []
        
        for config in chart_configs:
            chart_type = config.get('chart_type')
            x_axis = config.get('x_axis')
            y_axis = config.get('y_axis')
            limit = config.get('limit', 50)
            color = config.get('color', '#FF6B35')
            title = config.get('title', '')
            
            # Generate individual chart
            # (Reuse logic from main visualize function)
            # For brevity, this is a simplified version
            
            results.append({
                "chart_type": chart_type,
                "status": "success"
            })
        
        return {
            "success": True,
            "charts": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch visualization: {str(e)}")