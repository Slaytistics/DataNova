import openai
from openai import OpenAI

def summarize_dataset(df, api_key):
    client = OpenAI(api_key=api_key)

    sample_data = df.head(5).to_string(index=False)
    prompt = f"Give a plain-English summary of this dataset:\n\n{sample_data}"

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content
        return summary.strip()

    except Exception as e:
        return f"❌ GPT error: {e}"
