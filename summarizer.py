import requests
import streamlit as st
import pandas as pd


def summarize_dataset(df):
    """
    Generate an AI summary of the dataset using Together AI.
    Falls back to basic summary if AI fails.
    """
    
    # Get API key from secrets
    try:
        api_key = st.secrets["TOGETHER_API_KEY"]
    except Exception as e:
        print(f"⚠️  TOGETHER_API_KEY not found in secrets: {e}")
        return create_fallback_summary(df)
    
    # Prepare sample data
    sample_data = df.head(5).to_string(index=False)
    prompt = f"Give a plain-English summary of this dataset:\n\n{sample_data}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        print("🤖 Calling Together AI API...")
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=30  # Add timeout to prevent hanging
        )
        
        # Check if request was successful
        if response.status_code != 200:
            print(f"⚠️  API returned status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return create_fallback_summary(df)
        
        # Parse response JSON
        response_data = response.json()
        
        # Extract summary with multiple fallback methods
        summary = extract_summary_from_response(response_data)
        
        if summary:
            print("✅ AI summary generated successfully")
            return summary
        else:
            print("⚠️  Could not extract summary from response")
            return create_fallback_summary(df)
            
    except requests.exceptions.Timeout:
        print("⚠️  API request timed out")
        return create_fallback_summary(df)
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Network error: {e}")
        return create_fallback_summary(df)
    
    except KeyError as e:
        # This is the "choices" error
        print(f"⚠️  API response missing expected key: {e}")
        print(f"   Response structure: {response.json() if 'response' in locals() else 'N/A'}")
        return create_fallback_summary(df)
    
    except Exception as e:
        print(f"⚠️  Unexpected error in summarize_dataset: {e}")
        return create_fallback_summary(df)


def extract_summary_from_response(response_data):
    """
    Extract the summary text from Together AI response.
    Tries multiple methods to handle different response formats.
    """
    
    # Method 1: Standard format with choices
    try:
        if "choices" in response_data and len(response_data["choices"]) > 0:
            content = response_data["choices"][0]["message"]["content"]
            if content:
                return content.strip()
    except (KeyError, IndexError, TypeError) as e:
        print(f"   Method 1 (choices) failed: {e}")
    
    # Method 2: Alternative output field
    try:
        if "output" in response_data and response_data["output"]:
            return response_data["output"].strip()
    except (KeyError, TypeError) as e:
        print(f"   Method 2 (output) failed: {e}")
    
    # Method 3: Direct text field
    try:
        if "text" in response_data and response_data["text"]:
            return response_data["text"].strip()
    except (KeyError, TypeError) as e:
        print(f"   Method 3 (text) failed: {e}")
    
    # Method 4: Check for nested message
    try:
        if "message" in response_data and "content" in response_data["message"]:
            return response_data["message"]["content"].strip()
    except (KeyError, TypeError) as e:
        print(f"   Method 4 (message) failed: {e}")
    
    # If all methods fail, log the response structure
    print(f"⚠️  All extraction methods failed")
    print(f"   Response keys: {response_data.keys() if isinstance(response_data, dict) else 'Not a dict'}")
    
    return None


def create_fallback_summary(df: pd.DataFrame) -> str:
    """
    Create a basic summary when AI generation fails.
    This ensures the app always provides some summary.
    """
    try:
        # Get column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        # Build summary parts
        summary_parts = []
        
        # Basic info
        summary_parts.append(
            f"This dataset contains {len(df):,} rows and {len(df.columns)} columns."
        )
        
        # Numeric columns
        if numeric_cols:
            col_list = ', '.join(numeric_cols[:3])
            if len(numeric_cols) > 3:
                col_list += f", and {len(numeric_cols) - 3} more"
            summary_parts.append(
                f"It includes {len(numeric_cols)} numeric column{'s' if len(numeric_cols) != 1 else ''} ({col_list})."
            )
        
        # Text columns
        if text_cols:
            col_list = ', '.join(text_cols[:3])
            if len(text_cols) > 3:
                col_list += f", and {len(text_cols) - 3} more"
            summary_parts.append(
                f"It includes {len(text_cols)} text column{'s' if len(text_cols) != 1 else ''} ({col_list})."
            )
        
        # Datetime columns
        if datetime_cols:
            summary_parts.append(
                f"It includes {len(datetime_cols)} datetime column{'s' if len(datetime_cols) != 1 else ''}."
            )
        
        # General conclusion
        summary_parts.append(
            "The data appears to be structured tabular data suitable for analysis and visualization."
        )
        
        return ' '.join(summary_parts)
    
    except Exception as e:
        print(f"❌ Error creating fallback summary: {e}")
        # Ultimate fallback
        return f"Dataset with {len(df):,} rows and {len(df.columns)} columns."
