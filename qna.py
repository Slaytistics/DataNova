import requests
import streamlit as st
import pandas as pd


def ask_dataset_question(df: pd.DataFrame, question: str, mode: str = "Normal") -> str:
    """
    Answer questions about the dataset using Together AI.
    Falls back to basic answers if AI fails.
    
    Args:
        df: The dataset DataFrame
        question: User's question about the data
        mode: Analysis mode ("Normal", "Deep", "Quick")
    
    Returns:
        str: Answer to the question
    """
    
    # Get API key from secrets
    try:
        api_key = st.secrets["TOGETHER_API_KEY"]
    except Exception as e:
        print(f"⚠️  TOGETHER_API_KEY not found in secrets: {e}")
        return create_fallback_answer(df, question)
    
    # Prepare context about the dataset
    context = prepare_dataset_context(df, mode)
    
    # Prepare the full prompt
    prompt = f"""{context}

User Question: {question}

Please provide a clear, concise answer based on the dataset information above. If the question cannot be answered with the available data, explain what information would be needed."""

    # Adjust parameters based on mode
    max_tokens, temperature = get_mode_parameters(mode)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a data analysis assistant. Answer questions about datasets clearly and accurately based on the provided information."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        print(f"💬 Processing question: {question[:50]}...")
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=30
        )
        
        # Check if request was successful
        if response.status_code != 200:
            print(f"⚠️  API returned status code: {response.status_code}")
            return create_fallback_answer(df, question)
        
        # Parse response JSON
        response_data = response.json()
        
        # Extract answer with multiple fallback methods
        answer = extract_answer_from_response(response_data)
        
        if answer:
            print("✅ Answer generated successfully")
            return answer
        else:
            print("⚠️  Could not extract answer from response")
            return create_fallback_answer(df, question)
            
    except requests.exceptions.Timeout:
        print("⚠️  API request timed out")
        return create_fallback_answer(df, question)
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Network error: {e}")
        return create_fallback_answer(df, question)
    
    except KeyError as e:
        # This is the "choices" error
        print(f"⚠️  API response missing expected key: {e}")
        return create_fallback_answer(df, question)
    
    except Exception as e:
        print(f"⚠️  Unexpected error in ask_dataset_question: {e}")
        return create_fallback_answer(df, question)


def prepare_dataset_context(df: pd.DataFrame, mode: str) -> str:
    """Prepare context about the dataset based on the mode."""
    
    # Basic info
    row_count = len(df)
    col_count = len(df.columns)
    columns = df.columns.tolist()
    
    context_parts = [f"Dataset Overview:"]
    context_parts.append(f"- Total Rows: {row_count:,}")
    context_parts.append(f"- Total Columns: {col_count}")
    context_parts.append(f"- Column Names: {', '.join(columns)}")
    
    # Add more details based on mode
    if mode == "Deep":
        # More detailed analysis for Deep mode
        context_parts.append("\nColumn Details:")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            context_parts.append(f"  - {col}: type={dtype}, nulls={null_count}")
        
        # Add sample data
        context_parts.append("\nSample Data (first 5 rows):")
        context_parts.append(df.head(5).to_string(index=False))
        
    elif mode == "Quick":
        # Minimal context for Quick mode
        context_parts.append(f"\nColumn Types: {dict(df.dtypes)}")
        
    else:  # Normal mode
        # Moderate detail
        context_parts.append(f"\nColumn Types: {dict(df.dtypes)}")
        context_parts.append("\nSample Data (first 3 rows):")
        context_parts.append(df.head(3).to_string(index=False))
    
    return '\n'.join(context_parts)


def get_mode_parameters(mode: str) -> tuple:
    """Get max_tokens and temperature based on mode."""
    if mode == "Deep":
        return 500, 0.5  # More tokens, lower temperature for detailed analysis
    elif mode == "Quick":
        return 150, 0.8  # Fewer tokens, higher temperature for quick answers
    else:  # Normal
        return 300, 0.7  # Balanced parameters


def extract_answer_from_response(response_data):
    """
    Extract the answer text from Together AI response.
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
    
    return None


def create_fallback_answer(df: pd.DataFrame, question: str) -> str:
    """
    Create a basic answer when AI is unavailable.
    Tries to answer simple questions about the dataset.
    """
    
    question_lower = question.lower()
    
    # Handle common question types
    
    # How many rows/records?
    if any(word in question_lower for word in ['how many rows', 'how many records', 'number of rows', 'total rows']):
        return f"The dataset contains {len(df):,} rows."
    
    # How many columns?
    if any(word in question_lower for word in ['how many columns', 'number of columns', 'total columns']):
        return f"The dataset has {len(df.columns)} columns: {', '.join(df.columns.tolist())}."
    
    # What columns?
    if any(word in question_lower for word in ['what columns', 'list columns', 'column names', 'show columns']):
        return f"The dataset has these columns: {', '.join(df.columns.tolist())}."
    
    # Size of dataset
    if any(word in question_lower for word in ['size', 'how big', 'dimensions']):
        return f"The dataset has {len(df):,} rows and {len(df.columns)} columns."
    
    # Column types
    if any(word in question_lower for word in ['data types', 'column types', 'types of columns']):
        types_info = []
        for col in df.columns[:10]:  # First 10 columns
            types_info.append(f"- {col}: {df[col].dtype}")
        result = "Column data types:\n" + '\n'.join(types_info)
        if len(df.columns) > 10:
            result += f"\n... and {len(df.columns) - 10} more columns"
        return result
    
    # Missing values
    if any(word in question_lower for word in ['missing', 'null', 'nan', 'empty values']):
        null_counts = df.isnull().sum()
        if null_counts.sum() == 0:
            return "There are no missing values in this dataset."
        else:
            cols_with_nulls = null_counts[null_counts > 0]
            result = "Missing values found:\n"
            for col, count in cols_with_nulls.items():
                result += f"- {col}: {count} missing values\n"
            return result.strip()
    
    # Summary statistics
    if any(word in question_lower for word in ['summary', 'describe', 'statistics', 'stats']):
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            return f"The dataset has {len(numeric_cols)} numeric columns. You can explore statistics like mean, median, and standard deviation for columns: {', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''}."
        else:
            return "This dataset doesn't have any numeric columns for statistical summary."
    
    # Generic fallback
    return (
        f"I'm currently unable to provide a detailed answer. However, I can tell you that "
        f"the dataset contains {len(df):,} rows and {len(df.columns)} columns "
        f"({', '.join(df.columns.tolist()[:5])}{'...' if len(df.columns) > 5 else ''}). "
        f"Please try rephrasing your question or use one of these formats:\n"
        f"- 'How many rows are there?'\n"
        f"- 'What columns does this dataset have?'\n"
        f"- 'Are there any missing values?'"
    )