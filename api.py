from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from anywhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example endpoint for your frontend
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    # Replace this with your actual analysis logic
    result = "File received! Replace this with your logic."
    return {"result": result}
