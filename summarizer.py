import openai

def summarize_dataset(df, api_key):
    openai.api_key = api_key  # Correct way to set the key

    sample_data = df.head(5).to_string(index=False)
    prompt = f"Give a plain-English summary of this dataset:\n\n{sample_data}"

    try:
        response = openai.ChatCompletion.create(  # Correct method call
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ GPT error: {e}"
