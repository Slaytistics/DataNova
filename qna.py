import requests
import os
import pandas as pd

def ask_dataset_question(df: pd.DataFrame, question: str, mode: str = "Normal") -> str:
    """
    Analyzes user questions against the provided DataFrame using Together AI.
    Optimized for DataNova FastAPI backend.
    """
    
    # Use environment variables instead of Streamlit secrets for Render/Backend deployment
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("⚠️ TOGETHER_API_KEY not found in environment.")
        return create_fallback_answer(df, question)
    
    # 1. Prepare Context (Summary + Sample)
    context = prepare_dataset_context(df, mode)
    
    # 2. Build the Prompt
    prompt = f"""
    You are the DataNova AI Assistant. 
    Below is the context of a dataset currently uploaded by the user.
    
    {context}

    Question: {question}

    Instructions:
    - If the user asks for specific data points, refer to the 'Sample Data' provided.
    - If the question involves math/stats, use the 'Overview' counts.
    - Be conversational but professional.
    """

    max_tokens, temperature = get_mode_parameters(mode)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a helpful data analyst. Use the provided dataset metadata to answer user queries accurately."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=15 # Quicker timeout for better UX
        )
        
        if response.status_code == 200:
            res_json = response.json()
            # Clean extraction of the message
            return res_json["choices"][0]["message"]["content"].strip()
        else:
            return create_fallback_answer(df, question)
            
    except Exception as e:
        print(f"❌ Q&A Engine Error: {e}")
        return create_fallback_answer(df, question)

def prepare_dataset_context(df: pd.DataFrame, mode: str) -> str:
    """Creates a textual snapshot of the data for the AI's 'memory'."""
    row_count = len(df)
    cols = df.columns.tolist()
    
    # We provide a mix of metadata and actual values
    context = f"OVERVIEW:\n- Rows: {row_count}\n- Columns: {', '.join(cols)}\n"
    
    if mode == "Deep":
        # Deep mode includes data types and a larger sample
        context += f"DATA TYPES:\n{df.dtypes.to_string()}\n"
        context += f"SAMPLE DATA:\n{df.head(10).to_string()}"
    else:
        # Normal/Quick mode just gives a small preview
        context += f"SAMPLE DATA:\n{df.head(3).to_string()}"
        
    return context

def get_mode_parameters(mode: str):
    """Modes allow the user to control AI 'creativity'."""
    if mode == "Deep": return 600, 0.3 # Accurate, long
    if mode == "Quick": return 200, 0.8 # Creative, fast
    return 400, 0.6 # Balanced

def create_fallback_answer(df: pd.DataFrame, question: str) -> str:
    """Hardcoded logic to answer basic questions if the AI API fails."""
    q = question.lower()
    
    if "how many rows" in q or "count" in q:
        return f"The dataset contains {len(df)} rows."
    if "columns" in q or "names" in q:
        return f"The columns are: {', '.join(df.columns.tolist())}."
    if "missing" in q or "null" in q:
        nulls = df.isnull().sum().sum()
        return f"There are {nulls} missing values in the dataset."
        
    return "I'm having trouble connecting to my AI brain, but I can see you have a dataset with " + str(len(df.columns)) + " columns loaded. Ask me about the row count or column names!"