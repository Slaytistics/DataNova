from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import traceback

# Import your existing helper functions
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

# ✅ Updated Analyze route to handle Style, Insights, and Resources
@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...), 
    style: str = Form("Executive Summary") # <--- Added style parameter
):
    try:
        print(f"\n📊 Processing: {file.filename} | Style: {style}")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Please upload a .csv file.")
        
        df = pd.read_csv(file.file)

        # 1. Clean Data
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

        # 2. Convert numeric columns
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        row_count, col_count = df.shape
        columns = df.columns.tolist()

        # 3. Generate Content (Pass style to summarizer)
        try:
            # We assume your summarizer can take a 'style' argument
            summary_text = summarize_dataset(df.head(10), style=style)
        except Exception as e:
            print(f"⚠️ Summarizer error: {e}")
            summary_text = create_fallback_summary(df)

        # 4. Generate Insights & Resources
        # In a real app, you could have the AI generate these too.
        # For now, we generate them based on the dataset structure.
        insights = generate_actionable_insights(df, style)
        resources = generate_resource_links(df)

        # 5. Return Structured Response for Frontend
        return {
            "fileName": file.filename,
            "row_count": int(row_count),
            "column_count": int(col_count),
            "columns": columns,
            "summary": summary_text, # Frontend uses this as mainSummary
            "insights": insights,    # Required for the new UI
            "resources": resources,  # Required for the new UI
            "head": df.head(10).fillna("").to_dict(orient='records')
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_actionable_insights(df, style):
    """Generates simple logic-based insights based on the selected style."""
    insights = []
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if style == "Technical Analysis":
        insights.append(f"Data contains {len(num_cols)} numeric features for modeling.")
        insights.append("Recommendation: Check for multicollinearity between features.")
    elif style == "Business Insights":
        insights.append("Focus on high-value segments identified in the top records.")
        insights.append("Recommendation: Align Q3 strategy with identified growth trends.")
    else:
        insights.append("The dataset is well-structured for general reporting.")
        insights.append("Ensure missing values are handled before final presentation.")
        
    return insights

def generate_resource_links(df):
    """Suggests helpful links based on the columns found in the dataset."""
    resources = [
        {"title": "Pandas Documentation", "url": "https://pandas.pydata.org/docs/"},
        {"title": "Data Visualization Best Practices", "url": "https://www.tableau.com/learn/articles/data-visualization-tips"}
    ]
    
    # If it looks like financial data
    col_str = " ".join(df.columns).lower()
    if any(word in col_str for word in ['price', 'revenue', 'sales', 'budget']):
        resources.append({"title": "Financial Data Analysis Guide", "url": "https://www.investopedia.com/terms/f/financial-statement-analysis.asp"})
    
    # If it looks like health data
    if any(word in col_str for word in ['age', 'health', 'patient', 'bmi']):
        resources.append({"title": "Healthcare Analytics Basics", "url": "https://www.healthit.gov/topic/scientific-analysis-methods"})

    return resources

def create_fallback_summary(df: pd.DataFrame) -> str:
    return f"Dataset with {len(df):,} rows and {len(df.columns)} columns. Analysis focuses on {', '.join(df.columns[:3])}."

# ... Keep your existing /chart and /ask routes below ...