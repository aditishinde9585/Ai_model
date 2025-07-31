import os, requests, fitz
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
session = requests.Session()

def read_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        text = ""
        with fitz.open(filepath) as doc:
            for i, page in enumerate(doc):
                text += page.get_text()
                if i >= 4:  # ✅ Only first 5 pages
                    break
        return text[:5000]  # ✅ Limit characters
    elif ext == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()[:5000]
    return "Unsupported file type."

def get_llm_response(query, filepath, model):
    content = read_file(filepath)
    prompt = f"Answer concisely using the document:\n\n{content}\n\nQuery: {query}"

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    response = session.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=30)
    data = response.json()

    if "choices" not in data:
        return f"⚠️ LLM API error: {data.get('error', 'Unknown error')}"
    return data["choices"][0]["message"]["content"]