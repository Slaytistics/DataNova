from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import traceback
import io

# Import your helper functions
from summarizer import summarize_dataset
from figma_exporter import generate_figma_design_spec 
from visualizer import get_chart_suggestions
app = FastAPI()

# ✅ CORS Setup
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
        # 1. Load and Clean Data
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        
        # 2. Generate Content
        summary_text = summarize_dataset(df.head(15), style=style)

        # 3. Enhanced Insights
        insights = [
            f"Dataset consists of {len(df):,} rows and {len(df.columns)} variables.",
            f"Detected {df.select_dtypes(include=['number']).shape[1]} numeric columns and {df.select_dtypes(include=['object']).shape[1]} categorical columns.",
            "Recommended: Use 'Bar Charts' for categorical comparisons and 'Line Charts' for time-series data."
        ]
        
        # 4. Resources
        resources = [
            {"title": "Figma 'JSON to Design' Plugin", "url": "https://www.figma.com/community/plugin/1173443014168019313"},
            {"title": "DataNova Visualization Guide", "url": "#"}
        ]

        # 5. Figma Spec
        figma_spec = generate_figma_design_spec({
            "fileName": file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "summary": summary_text
        })

        # 6. Chart Suggestions (For the Visualizer page)
        chart_configs = get_chart_suggestions(df)

        return {
            "fileName": file.filename,
            "row_count": int(len(df)),
            "column_count": int(len(df.columns)),
            "columns": df.columns.tolist(),
            "summary": summary_text,
            "insights": insights,
            "resources": resources,
            "figma_spec": figma_spec,
            "chart_configs": chart_configs,
            "head": df.head(10).fillna("").to_dict(orient='records')
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# --- NEW: AI CHAT ASSISTANT ENDPOINT ---
@app.post("/chat")
async def chat_with_data(payload: dict):
    """
    Handles queries from the AIAssistant component.
    Expects: {"message": "user text", "context": {...dataset info...}}
    """
    try:
        query = payload.get("message", "").lower()
        context = payload.get("context", {})
        
        # Logic for Data-Specific Questions
        if "column" in query:
            cols = ", ".join(context.get("columns", []))
            return {"response": f"Your dataset has {len(context.get('columns', []))} columns: {cols}."}
        
        if "rows" in query or "size" in query:
            return {"response": f"This dataset contains exactly {context.get('row_count')} entries."}

        if "figma" in query:
            return {"response": "To export to Figma, go to the Export page. I've already prepared a JSON spec based on your data columns!"}

        if "visual" in query or "chart" in query:
            return {"response": "I can help! Head over to the Visualizer tab. I recommend a Bar Chart for your categorical data."}

        # Default fallback
        return {"response": "That's a great question about your data. Based on the summary, this file focuses on " + context.get("summary", "general trends")[:100] + "..."}
    
    except Exception as e:
        return {"response": "I'm having trouble processing that data point. Could you rephrase?"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)