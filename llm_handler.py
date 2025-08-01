# llm_handler.py
import os
import requests
import fitz  # PyMuPDF
import docx
import email
from email import policy
from email.parser import BytesParser
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

DEFAULT_MODEL = "mistralai/mistral-7b-instruct"

def read_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return read_pdf(filepath)
    elif ext == ".txt":
        return read_txt(filepath)
    elif ext == ".docx":
        return read_docx(filepath)
    elif ext == ".eml":
        return read_eml(filepath)
    return "Unsupported file type."

def read_pdf(filepath):
    text = ""
    with fitz.open(filepath) as doc:
        for i, page in enumerate(doc):
            text += page.get_text()
            if i >= 4:
                break
    return text[:5000]

def read_txt(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()[:5000]

def read_docx(filepath):
    doc = docx.Document(filepath)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text[:5000]

def read_eml(filepath):
    with open(filepath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
        try:
            body = msg.get_body(preferencelist=('plain'))
            return body.get_content()[:5000] if body else "No plain text content found in email."
        except:
            return "Failed to extract email content."

def get_llm_response(query, filepath, model=DEFAULT_MODEL):
    content = read_file(filepath)
    prompt = f"""You are a helpful assistant. Based on the following document, answer this query:

Document:
{content}

Query:
{query}"""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
    data = response.json()
    if "choices" not in data:
        raise ValueError(f"LLM API error: {data.get('error', 'Unknown error')}")
    return data['choices'][0]['message']['content']