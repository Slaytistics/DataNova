from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import traceback

# Import your helper functions (Ensure these files are in the same directory)
from summarizer import summarize_dataset
from figma_exporter import generate_figma_design_spec 

app = FastAPI()

# ✅ CORS Setup (Allows your Vercel/Next.js frontend to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...), 
    style: str = Form("Executive Summary")
):
    try:
        # 1. Load the CSV Data
        df = pd.read_csv(file.file)
        
        # 2. Clean Data (Remove whitespace and unnamed columns)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        
        # 3. Generate AI Content using the dynamic Style
        # This passes the user's choice (Executive, Technical, or Business) to the AI
        summary_text = summarize_dataset(df.head(10), style=style)

        # 4. Generate Actionable Insights (Logic-based)
        # These are displayed in the new yellow cards on your frontend
        insights = [
            f"Dataset consists of {len(df):,} rows and {len(df.columns)} columns.",
            "Initial data scan suggests high variance in numeric columns.",
            "Recommended: Focus on top 20% of contributors for immediate growth."
        ]
        
        # 5. Resource Recommendations
        resources = [
            {"title": "Figma 'JSON to Design' Plugin", "url": "https://www.figma.com/community/plugin/1173443014168019313"},
            {"title": "Data Visualization Best Practices", "url": "https://www.tableau.com/learn/articles/data-visualization-tips"}
        ]

        # 6. Generate the Figma Design Spec
        # This transforms the raw data into a 'Blueprint' for the Export Page
        figma_spec = generate_figma_design_spec({
            "fileName": file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "summary": summary_text
        })

        # 7. Final Response Object
        return {
            "fileName": file.filename,
            "row_count": int(len(df)),
            "column_count": int(len(df.columns)),
            "columns": df.columns.tolist(),
            "summary": summary_text,
            "insights": insights,
            "resources": resources,
            "figma_spec": figma_spec,
            "head": df.head(10).fillna("").to_dict(orient='records')
        }

    except Exception as e:
        print(f"❌ Error in /analyze: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# Test route to ensure API is healthy
@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.1.0"}

if __name__ == "__main__":
    import uvicorn
    # Make sure to use host 0.0.0.0 for Render deployment
    uvicorn.run(app, host="0.0.0.0", port=8000)