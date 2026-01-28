import requests
import pandas as pd
import os

def summarize_dataset(df, style="Executive Summary"):
    """
    Generate an AI summary of the dataset using Together AI with specific styles.
    Optimized for DataNova FastAPI backend.
    """
    
    # Get API key from Environment variables (Required for Render/Deployment)
    api_key = os.getenv("TOGETHER_API_KEY")
    
    # If no API key is found, trigger fallback immediately to prevent server crash
    if not api_key:
        print("⚠️ TOGETHER_API_KEY not found. Using fallback logic.")
        return create_fallback_summary(df)
    
    # 1. Logic-based instructions
    style_prompts = {
        "Executive Summary": "Provide a high-level overview for executives. Focus on the 'big picture' and overall health of the data.",
        "Technical Analysis": "Provide a deep technical dive. Focus on data types, distributions, and statistical integrity.",
        "Business Insights": "Focus on actionable business value. Identify 2-3 specific trends that could impact operations."
    }
    
    selected_instruction = style_prompts.get(style, style_prompts["Executive Summary"])
    
    # 2. Token Optimization: Sample enough to be smart, but small enough to be fast
    # We take the head and basic stats to give the AI more context
    sample_data = df.head(5).to_string(index=False)
    data_description = df.describe().to_string()

    full_prompt = (
        f"Role: Expert Data Analyst\n"
        f"Task: {selected_instruction}\n\n"
        f"Dataset Columns: {', '.join(df.columns.tolist())}\n"
        f"Data Sample:\n{sample_data}\n\n"
        f"Statistical Context:\n{data_description}\n\n"
        f"Format: Use Markdown bullet points. Keep response under 250 words."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a specialized data assistant for the DataNova platform."},
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.5 # Lower temperature for more factual, stable analysis
    }

    try:
        # 10-second timeout is safer for a web API response
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=15 
        )
        
        if response.status_code == 200:
            response_data = response.json()
            summary = response_data["choices"][0]["message"]["content"].strip()
            return summary
        else:
            print(f"⚠️ API Status Error: {response.status_code}")
            return create_fallback_summary(df)
            
    except Exception as e:
        print(f"⚠️ AI Request Failed: {e}")
        return create_fallback_summary(df)

def create_fallback_summary(df: pd.DataFrame) -> str:
    """Statistical fallback if AI is unavailable."""
    num_rows, num_cols = df.shape
    num_cols_list = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols_list = df.select_dtypes(include=['object']).columns.tolist()
    
    summary = f"**Dataset Overview**\n"
    summary += f"The uploaded file contains {num_rows} records and {num_cols} unique variables.\n\n"
    summary += f"- **Quantitative Fields:** {len(num_cols_list)} detected ({', '.join(num_cols_list[:3])}...)\n"
    summary += f"- **Qualitative Fields:** {len(cat_cols_list)} detected ({', '.join(cat_cols_list[:3])}...)\n\n"
    summary += "AI insights are currently generating based on the statistical distribution above."
    
    return summary