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

# ✅ CORS (allow frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Test route
@app.get("/")
def home():
    return {
        "message": "DataNova API is running",
        "status": "healthy",
        "version": "2.0.0",
        "endpoints": {
            "analyze": "/analyze (POST)",
            "chart": "/chart (POST)",
            "ask": "/ask (POST)"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "api_version": "2.0.0"
    }

# ✅ Analyze route (IMPROVED WITH ERROR HANDLING)
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        print(f"\n📊 Processing file: {file.filename}")
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported. Please upload a .csv file."
            )
        
        # 1. Read the CSV
        df = pd.read_csv(file.file)
        print(f"   Initial shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

        # 2. Clean Data (Strip whitespace, remove unnamed columns)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        print(f"   After cleaning: {df.shape[0]:,} rows × {df.shape[1]} columns")

        # 3. Convert numeric columns where possible
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # 4. Get Basic Stats
        row_count, col_count = df.shape
        columns = df.columns.tolist()
        
        print(f"   Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")

        # 5. Get Top 10 Entries for Preview (Handle NaNs for JSON safety)
        head = df.head(10).fillna("").to_dict(orient='records')

        # 6. Generate AI Summary (IMPROVED ERROR HANDLING)
        summary = "Summary unavailable."
        try:
            print("🤖 Generating AI summary...")
            # Pass a sample to the summarizer
            summary = summarize_dataset(df.head(10))
            print("✅ AI summary generated successfully")
            
        except AttributeError as e:
            # This is the 'choices' error
            print(f"⚠️  Together AI API response format issue: {e}")
            summary = create_fallback_summary(df)
            print("📝 Using fallback summary instead")
            
        except KeyError as e:
            # Missing keys in API response
            print(f"⚠️  Together AI API key error: {e}")
            summary = create_fallback_summary(df)
            print("📝 Using fallback summary instead")
            
        except Exception as e:
            # Any other error
            print(f"⚠️  Summarizer error: {e}")
            print(f"   Error type: {type(e).__name__}")
            summary = create_fallback_summary(df)
            print("📝 Using fallback summary instead")

        # 7. Return the Structure the Frontend Expects
        response = {
            "fileName": file.filename,
            "row_count": int(row_count),
            "column_count": int(col_count),
            "columns": columns,
            "summary": summary,
            "head": head
        }
        
        print(f"✅ Analysis complete!\n")
        return response

    except pd.errors.EmptyDataError:
        print("❌ Error: Empty CSV file")
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty. Please upload a valid CSV file with data."
        )
    
    except pd.errors.ParserError as e:
        print(f"❌ CSV parsing error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Unable to parse CSV file. Please check the file format."
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"❌ Unexpected error in /analyze: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


def create_fallback_summary(df: pd.DataFrame) -> str:
    """
    Create a basic summary when AI generation fails.
    This ensures the app always works even if Together AI has issues.
    """
    try:
        # Get column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Build summary
        summary_parts = []
        summary_parts.append(f"This dataset contains {len(df):,} rows and {len(df.columns)} columns.")
        
        if numeric_cols:
            summary_parts.append(
                f"It includes {len(numeric_cols)} numeric column{'s' if len(numeric_cols) != 1 else ''} "
                f"({', '.join(numeric_cols[:3])}{'...' if len(numeric_cols) > 3 else ''})."
            )
        
        if text_cols:
            summary_parts.append(
                f"It includes {len(text_cols)} text column{'s' if len(text_cols) != 1 else ''} "
                f"({', '.join(text_cols[:3])}{'...' if len(text_cols) > 3 else ''})."
            )
        
        summary_parts.append("The data appears to be structured tabular data suitable for analysis.")
        
        return ' '.join(summary_parts)
    
    except Exception as e:
        print(f"❌ Error creating fallback summary: {str(e)}")
        return f"Dataset with {len(df):,} rows and {len(df.columns)} columns."


# ✅ Chart route (IMPROVED ERROR HANDLING)
@app.post("/chart")
async def chart(
    file: UploadFile = File(...),
    column: str = Form(...),
    top_n: int = Form(10)
):
    try:
        print(f"\n📈 Generating chart for column: {column}")
        
        # Read and clean CSV
        df = pd.read_csv(file.file)
        df.columns = [col.strip() for col in df.columns]
        
        # Validate column exists
        if column not in df.columns:
            available_cols = ', '.join(df.columns[:5])
            raise HTTPException(
                status_code=400,
                detail=f"Column '{column}' not found. Available columns: {available_cols}..."
            )
        
        # Generate chart
        fig = plot_top_column(df, column, top_n=top_n)
        print(f"✅ Chart generated successfully\n")
        
        return fig.to_dict()
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"❌ Error generating chart: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating chart: {str(e)}"
        )


# ✅ Ask question route (IMPROVED ERROR HANDLING)
@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...),
    mode: str = Form("Normal")
):
    try:
        print(f"\n💬 Question: {question}")
        print(f"   Mode: {mode}")
        
        # Read and clean CSV
        df = pd.read_csv(file.file)
        df.columns = [col.strip() for col in df.columns]
        
        # Get answer from Q&A system
        answer = ask_dataset_question(df, question, mode=mode)
        print(f"✅ Answer generated\n")
        
        return {"answer": answer}
    
    except AttributeError as e:
        # Handle Together AI 'choices' error in Q&A
        print(f"⚠️  Together AI error in Q&A: {e}")
        return {
            "answer": "I'm experiencing technical difficulties with the AI service. Please try rephrasing your question or try again later."
        }
    
    except Exception as e:
        print(f"❌ Error answering question: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting DataNova Backend Server...")
    print("   Features: Analyze, Chart, Q&A")
    uvicorn.run(app, host="0.0.0.0", port=8000)