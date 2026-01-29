from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from summarizer import router as summary_router
from visualizer import router as visualizer_router
from qna import router as qna_router

app = FastAPI(
    title="DataNova API", 
    version="3.0",
    description="Complete data analysis, visualization, and Q&A platform"
)

# ---------------- CORS MIDDLEWARE ---------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTERS ---------------- #
# All routes are prefixed with /api
app.include_router(summary_router, prefix="/api", tags=["Summarizer"])
app.include_router(visualizer_router, prefix="/api", tags=["Visualizer"])
app.include_router(qna_router, prefix="/api", tags=["Q&A"])


# ---------------- ROOT & HEALTH ENDPOINTS ---------------- #
@app.get("/", tags=["Root"])
def root():
    """Root endpoint - API status check"""
    return {
        "message": "DataNova Backend Running Successfully",
        "version": "3.0",
        "status": "operational",
        "endpoints": {
            "summarizer": "/api/summary",
            "visualizer": "/api/visualize",
            "column_analysis": "/api/analyze-columns",
            "qna": "/api/qna"
        }
    }

@app.get("/health", tags=["Root"])
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.0",
        "service": "DataNova API"
    }


# ---------------- STARTUP EVENT ---------------- #
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 50)
    print("🚀 DataNova API Starting...")
    print("=" * 50)
    print("📊 Summarizer: /api/summary")
    print("📈 Visualizer: /api/visualize")
    print("📋 Column Analysis: /api/analyze-columns")
    print("❓ Q&A: /api/qna")
    print("=" * 50)


# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )