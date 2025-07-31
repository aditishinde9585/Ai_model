import os
import requests
import fitz  # from PyMuPDF
from dotenv import load_dotenv

# Load environment variables from .env (used in local dev, ignored on Render)
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("OPENROUTER_API_KEY")
session = requests.Session()

def read_file(filepath):
    """
    Reads content from PDF or TXT file.
    Limits: First 5 pages of PDF or first 5000 characters of TXT.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        text = ""
        try:
            with fitz.open(filepath) as doc:
                for i, page in enumerate(doc):
                    text += page.get_text()
                    if i >= 4:  # ✅ First 5 pages only
                        break
        except Exception as e:
            return f"⚠️ Error reading PDF: {str(e)}"
        return text[:5000]

    elif ext == '.txt':
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()[:5000]
        except Exception as e:
            return f"⚠️ Error reading TXT: {str(e)}"

    return "⚠️ Unsupported file type. Please upload a .pdf or .txt file."


def get_llm_response(query, filepath, model):
    """
    Sends query and file context to OpenRouter LLM API.
    """
    if not API_KEY:
        return "⚠️ OPENROUTER_API_KEY is missing from environment variables."

    content = read_file(filepath)
    if content.startswith("⚠️"):
        return content  # return early if file couldn't be read

    prompt = f"Answer concisely using the document:\n\n{content}\n\nQuery: {query}"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        data = response.json()
        if "choices" not in data:
            return f"⚠️ LLM API error: {data.get('error', 'Unknown error')}"
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"⚠️ Request error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"
