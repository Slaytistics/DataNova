import requests
import streamlit as st
import pandas as pd
import os

def summarize_dataset(df, style="Executive Summary"):
    """
    Generate an AI summary of the dataset using Together AI with specific styles.
    Supports: 'Executive Summary', 'Technical Analysis', 'Business Insights'
    """
    
    # Get API key (Check Streamlit secrets first, then Environment variables for Render)
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["TOGETHER_API_KEY"]
        except:
            print("⚠️ TOGETHER_API_KEY not found. Using fallback.")
            return create_fallback_summary(df)
    
    # 1. Customize the prompt based on the style
    style_prompts = {
        "Executive Summary": "Provide a high-level overview for executives. Focus on the 'big picture', key metrics, and overall health of the data. Keep it professional and concise.",
        "Technical Analysis": "Provide a deep technical dive. Focus on data types, potential correlations, missing value patterns, and statistical distributions. Use data science terminology.",
        "Business Insights": "Focus on actionable business value. Identify trends that could impact revenue, customer behavior, or operational efficiency. Provide 2-3 specific recommendations."
    }
    
    selected_instruction = style_prompts.get(style, style_prompts["Executive Summary"])
    
    # Prepare sample data (limited to 5 rows to save tokens)
    sample_data = df.head(5).to_string(index=False)
    
    full_prompt = (
        f"Context: {selected_instruction}\n\n"
        f"Dataset Columns: {', '.join(df.columns.tolist())}\n"
        f"Dataset Sample:\n{sample_data}\n\n"
        f"Output Requirements:\n"
        f"- Use plain English.\n"
        f"- Format with bullet points for readability.\n"
        f"- Be specific to the columns provided."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are an expert Data Analyst and Business Consultant."},
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 400, # Increased to allow for detailed insights
        "temperature": 0.6
    }

    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return create_fallback_summary(df)
        
        response_data = response.json()
        summary = extract_summary_from_response(response_data)
        
        return summary if summary else create_fallback_summary(df)
            
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return create_fallback_summary(df)

def extract_summary_from_response(response_data):
    """Safely extracts content from various AI response formats."""
    try:
        return response_data["choices"][0]["message"]["content"].strip()
    except:
        try:
            return response_data.get("output", None)
        except:
            return None

def create_fallback_summary(df: pd.DataFrame) -> str:
    """Basic structural summary if AI fails."""
    num_rows, num_cols = df.shape
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    summary = f"### Dataset Overview\n"
    summary += f"This dataset contains **{num_rows} rows** and **{num_cols} columns**.\n\n"
    summary += f"**Key Columns:** {', '.join(df.columns[:5])}...\n\n"
    summary += f"**Analysis:** The data contains {len(numeric_cols)} numeric fields. "
    summary += "The structure is suitable for further trend analysis and visualization."
    
    return summary
