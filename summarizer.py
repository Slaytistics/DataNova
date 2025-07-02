import requests

def summarize_dataset(df, api_key):
    sample_data = df.head(7).to_string(index=False)
    columns = ", ".join(df.columns)

    prompt = (
        f"You are an AI data analyst. This dataset has the following columns:\n{columns}\n\n"
        f"Here are sample rows:\n{sample_data}\n\n"
        "Write a short, plain English summary of what the dataset is about. "
        "Mention any trends, interesting values, or what type of data it appears to be."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/Slaytistics/Datalicious",  # your repo
        "X-Title": "datalicious-app",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",  # can change to claude-3-haiku etc.
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    result = response.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return f"❌ GPT error:\n{result.get('error', {}).get('message', 'Unknown error')}"
