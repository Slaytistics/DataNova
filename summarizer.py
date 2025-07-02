import requests

def summarize_dataset(df, api_key):
    sample_data = df.head(5).to_string(index=False)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/GAMINGISFUN/Datalicious",  
        "X-Title": "datalicious-app",
        "Content-Type": "application/json"
    }

    prompt = f"Give a plain-English summary of this dataset:\n\n{sample_data}"

    data = {
        "model": "mistralai/mistral-7b-instruct",  # You can swap for other OpenRouter models
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response_json = response.json()

    if "choices" in response_json:
        return response_json["choices"][0]["message"]["content"]
    else:
        return "❌ GPT error: " + str(response_json)
