import requests
import pandas as pd
import os
import io
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from typing import Optional

router = APIRouter()

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"


# ---------------- ENHANCED SUMMARY ENDPOINT ---------------- #

@router.post("/summary")
async def summarize_dataset(request: Request):
    """
    Enhanced summary endpoint supporting:
    1. New CSV file uploads (multipart/form-data)
    2. Regeneration with existing data (application/json)
    3. Customizable length, tone, and audience
    """
    content_type = request.headers.get("content-type", "")
    
    try:
        # Handle JSON request (regeneration with existing data)
        if "application/json" in content_type:
            data = await request.json()
            existing_data = data.get('existingData')
            length = data.get('length', 'medium')
            tone = data.get('tone', 'professional')
            audience = data.get('audience', 'general')
            style = data.get('style', 'Executive Summary')
            
            if not existing_data:
                raise HTTPException(status_code=400, detail="No existingData provided")
            
            df_info = existing_data.get('dataInfo')
            if not df_info:
                raise HTTPException(status_code=400, detail="No dataInfo found in existingData")
            
            # Regenerate summary with new preferences
            summary_text, mode = await generate_summary_from_info(
                df_info, length, tone, audience, style
            )
            
            # Return updated response
            return {
                "fileName": df_info.get('filename', 'Unknown'),
                "row_count": df_info.get('rows', 0),
                "column_count": df_info.get('columns', 0),
                "columns": df_info.get('column_names', []),
                "head": df_info.get('head_data', []),
                "summary": summary_text,
                "mode": mode,
                "insights": generate_insights(df_info),
                "resources": generate_resources(audience, tone),
                "dataInfo": df_info,
                "preferences": {
                    "length": length,
                    "tone": tone,
                    "audience": audience
                }
            }
        
        # Handle multipart/form-data request (new file upload)
        else:
            form = await request.form()
            file = form.get('file')
            length = form.get('length', 'medium')
            tone = form.get('tone', 'professional')
            audience = form.get('audience', 'general')
            style = form.get('style', 'Executive Summary')
            
            if not file:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Verify it's a CSV file
            if not file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="Only CSV files are supported")
            
            # Read and process CSV
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))
            df.columns = df.columns.str.strip()

            # Store original data info
            original_row_count = len(df)
            original_column_count = len(df.columns)
            columns = df.columns.tolist()
            head_data = df.head(10).to_dict(orient='records')

            # Create comprehensive data info for storage
            df_info = {
                'filename': file.filename,
                'rows': original_row_count,
                'columns': original_column_count,
                'column_names': columns,
                'head_data': head_data,
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'missing_values': df.isnull().sum().to_dict(),
                'numeric_columns': df.select_dtypes(include=["number"]).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=["object"]).columns.tolist(),
            }

            # Sample for AI analysis
            if len(df) > 5000:
                df_sample = df.sample(5000)
            else:
                df_sample = df

            # Add sample statistics to df_info
            df_info['sample_data'] = df_sample.head(5).to_string(index=False)
            df_info['statistics'] = df_sample.describe().round(2).to_string()

            # Generate AI summary
            summary_text, mode = await generate_summary_from_info(
                df_info, length, tone, audience, style
            )

            # Generate insights and resources
            insights = generate_insights(df_info)
            resources = generate_resources(audience, tone)

            # Return complete response
            return {
                "fileName": file.filename,
                "row_count": original_row_count,
                "column_count": original_column_count,
                "columns": columns,
                "head": head_data,
                "summary": summary_text,
                "mode": mode,
                "insights": insights,
                "resources": resources,
                "stats": {
                    "Rows": original_row_count,
                    "Columns": original_column_count,
                    "Missing Values": sum(df.isnull().sum().to_dict().values())
                },
                "dataInfo": df_info,
                "preferences": {
                    "length": length,
                    "tone": tone,
                    "audience": audience
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in summarize_dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


# ---------------- GENERATE SUMMARY WITH CUSTOMIZATION ---------------- #

async def generate_summary_from_info(
    df_info: dict,
    length: str,
    tone: str,
    audience: str,
    style: str = "Executive Summary"
) -> tuple[str, str]:
    """
    Generate AI summary with customization options
    Returns: (summary_text, mode)
    """
    api_key = os.getenv("TOGETHER_API_KEY")
    
    if not api_key:
        return create_fallback_summary(df_info), "fallback"

    # Build customized prompt
    prompt = build_custom_prompt(df_info, length, tone, audience, style)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Adjust max_tokens based on length
    token_limits = {
        "concise": 300,
        "medium": 500,
        "lengthy": 800
    }
    max_tokens = token_limits.get(length, 500)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": get_system_prompt(tone, audience)},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.4 if tone == "professional" else 0.6
    }

    try:
        response = requests.post(
            TOGETHER_API_URL,
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            summary_text = data["choices"][0]["message"]["content"]
            return summary_text, "ai"
        else:
            print(f"AI API Error: Status {response.status_code}")
            return create_fallback_summary(df_info), "fallback"
            
    except Exception as api_error:
        print(f"AI API Error: {api_error}")
        return create_fallback_summary(df_info), "fallback"


# ---------------- BUILD CUSTOM PROMPT ---------------- #

def build_custom_prompt(
    df_info: dict,
    length: str,
    tone: str,
    audience: str,
    style: str
) -> str:
    """Build a customized prompt based on user preferences"""
    
    # Length instructions
    length_instructions = {
        "concise": "Provide a brief, concise summary in 2-3 paragraphs (150-200 words). Focus only on the most critical insights.",
        "medium": "Provide a comprehensive summary in 4-5 paragraphs (300-400 words). Cover key patterns, statistics, and recommendations.",
        "lengthy": "Provide an in-depth, detailed summary in 6-8 paragraphs (500-700 words). Include thorough analysis, multiple perspectives, and detailed recommendations."
    }
    
    # Tone instructions
    tone_instructions = {
        "professional": "Use professional, formal language suitable for business reports and stakeholder presentations.",
        "technical": "Use technical terminology, statistical language, and data science concepts. Include technical details about distributions, correlations, and data quality.",
        "casual": "Use conversational, easy-to-understand language. Avoid jargon and explain concepts in simple terms."
    }
    
    # Audience instructions
    audience_instructions = {
        "general": "Write for a general audience with basic data literacy. Explain technical terms when used.",
        "executive": "Write for C-suite executives and business leaders. Focus on business impact, ROI, strategic insights, and actionable recommendations.",
        "technical": "Write for data scientists, engineers, and technical professionals. Include statistical rigor, methodological considerations, and technical implementation details.",
        "academic": "Write for researchers and academics. Focus on methodology, statistical validity, research implications, and scholarly rigor."
    }

    # Get sample data and statistics
    sample_data = df_info.get('sample_data', 'Not available')
    statistics = df_info.get('statistics', 'Not available')
    columns = df_info.get('column_names', [])
    rows = df_info.get('rows', 0)
    cols = df_info.get('columns', 0)
    missing = df_info.get('missing_values', {})
    
    prompt = f"""You are analyzing a dataset with the following information:

**Dataset Overview:**
- Filename: {df_info.get('filename', 'Unknown')}
- Rows: {rows:,}
- Columns: {cols}
- Column Names: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}

**Sample Data (first 5 rows):**
{sample_data}

**Statistical Summary:**
{statistics}

**Data Quality:**
- Missing Values: {sum(missing.values())} total
- Columns with Missing Data: {', '.join([k for k, v in missing.items() if v > 0][:5])}

**Task:**
{length_instructions.get(length, length_instructions['medium'])}
{tone_instructions.get(tone, tone_instructions['professional'])}
{audience_instructions.get(audience, audience_instructions['general'])}

**Your summary should include:**
1. Overview of what the dataset represents and its purpose
2. Key patterns, trends, and notable findings
3. Important statistics or outliers
4. Data quality observations
5. Business or research implications (depending on audience)
6. Recommendations for further analysis or action

**Additional context:** {style}

Write a well-structured, coherent summary that follows the specified length, tone, and audience requirements.
"""
    
    return prompt


# ---------------- SYSTEM PROMPT ---------------- #

def get_system_prompt(tone: str, audience: str) -> str:
    """Get customized system prompt based on tone and audience"""
    
    base = "You are DataNova AI, a professional data analysis assistant."
    
    tone_contexts = {
        "professional": "You communicate in a formal, business-appropriate manner.",
        "technical": "You are a technical expert who speaks the language of data scientists and engineers.",
        "casual": "You explain complex data insights in simple, conversational language."
    }
    
    audience_contexts = {
        "general": "Your audience has basic data literacy.",
        "executive": "Your audience consists of business leaders who need actionable insights.",
        "technical": "Your audience consists of data professionals who understand advanced analytics.",
        "academic": "Your audience consists of researchers who value methodological rigor."
    }
    
    return f"{base} {tone_contexts.get(tone, '')} {audience_contexts.get(audience, '')}"


# ---------------- GENERATE INSIGHTS ---------------- #

def generate_insights(df_info: dict) -> list[str]:
    """Generate key takeaways based on data analysis"""
    
    insights = []
    
    rows = df_info.get('rows', 0)
    cols = df_info.get('columns', 0)
    missing = df_info.get('missing_values', {})
    numeric_cols = df_info.get('numeric_columns', [])
    cat_cols = df_info.get('categorical_columns', [])
    
    # Dataset size insight
    if rows > 10000:
        insights.append(f"Large dataset with {rows:,} rows provides substantial statistical power for analysis")
    elif rows < 100:
        insights.append(f"Small dataset ({rows} rows) may require careful interpretation of results")
    
    # Data completeness
    total_missing = sum(missing.values())
    if total_missing == 0:
        insights.append("Complete dataset with no missing values - excellent data quality")
    elif total_missing > rows * 0.1:
        insights.append(f"Significant missing data detected ({total_missing:,} values) - may require imputation")
    
    # Column diversity
    if len(numeric_cols) > len(cat_cols):
        insights.append(f"Predominantly numerical data ({len(numeric_cols)} numeric vs {len(cat_cols)} categorical columns) - suitable for quantitative analysis")
    elif len(cat_cols) > len(numeric_cols):
        insights.append(f"Rich categorical data ({len(cat_cols)} categorical columns) - consider segmentation analysis")
    
    # Add a general insight
    insights.append(f"Dataset contains {cols} features across {rows:,} observations, enabling multi-dimensional analysis")
    
    return insights[:5]  # Return max 5 insights


# ---------------- GENERATE RESOURCES ---------------- #

def generate_resources(audience: str, tone: str) -> list[dict]:
    """Generate recommended reading based on audience and tone"""
    
    resources_map = {
        "general": [
            {"title": "Introduction to Data Analysis", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
            {"title": "Data Visualization Best Practices", "url": "https://www.tableau.com/learn/articles/data-visualization"},
        ],
        "executive": [
            {"title": "Data-Driven Decision Making for Leaders", "url": "https://hbr.org/topic/data"},
            {"title": "Business Analytics Fundamentals", "url": "https://www.forbes.com/sites/bernardmarr/"},
        ],
        "technical": [
            {"title": "Advanced Statistical Methods", "url": "https://scikit-learn.org/stable/tutorial/index.html"},
            {"title": "Data Science Best Practices", "url": "https://github.com/topics/data-science"},
        ],
        "academic": [
            {"title": "Statistical Analysis in Research", "url": "https://www.r-project.org/"},
            {"title": "Research Data Management", "url": "https://www.nature.com/sdata/"},
        ]
    }
    
    return resources_map.get(audience, resources_map["general"])


# ---------------- FALLBACK SUMMARY ---------------- #

def create_fallback_summary(df_info: dict) -> str:
    """Create fallback summary when AI is unavailable"""
    
    rows = df_info.get('rows', 0)
    cols = df_info.get('columns', 0)
    num_cols = df_info.get('numeric_columns', [])
    cat_cols = df_info.get('categorical_columns', [])
    missing = df_info.get('missing_values', {})
    total_missing = sum(missing.values())

    summary = f"""
**Dataset Overview**
This dataset contains {rows:,} rows and {cols} columns, providing a {'substantial' if rows > 1000 else 'modest'} amount of data for analysis.

**Column Composition**
- Numeric Columns ({len(num_cols)}): {', '.join(num_cols[:5])}{'...' if len(num_cols) > 5 else ''}
- Categorical Columns ({len(cat_cols)}): {', '.join(cat_cols[:5])}{'...' if len(cat_cols) > 5 else ''}

**Data Quality**
- Missing Values: {total_missing:,} ({(total_missing / (rows * cols) * 100):.1f}% of total data)
- Columns Affected: {len([k for k, v in missing.items() if v > 0])}

**Recommendations**
{'Address missing data through imputation or removal.' if total_missing > 0 else 'Data is complete and ready for analysis.'} Consider exploratory data analysis to identify patterns and relationships between variables.

*Note: This summary was generated using statistical analysis. For AI-powered insights, please configure the Together API key.*
"""
    return summary.strip()