from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from summarizer import router as summary_router
from visualizer import router as visualizer_router
from qna import router as qna_router

app = FastAPI(title="DataNova API", version="3.0")

# ---------------- CORS ---------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to your Vercel domain later
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTERS ---------------- #
app.include_router(summary_router, prefix="/api")
app.include_router(visualizer_router, prefix="/api")
app.include_router(qna_router, prefix="/api")


# ---------------- ROOT ---------------- #
@app.get("/")
def root():
    return {"message": "DataNova Backend Running Successfully"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "3.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
