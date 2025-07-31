from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from llm_handler import get_llm_response

app = FastAPI()
templates = Jinja2Templates(directory="templates")
UPLOAD_FOLDER = "uploads/"
DEFAULT_MODEL = "qwen/qwen3-coder:free"

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/query")
async def query_api(query: str = Form(...), document: UploadFile = None):
    # ✅ Ensure a valid file is uploaded
    if document is None or document.filename == "":
        return JSONResponse(content={"error": "No file uploaded"}, status_code=400)

    # ✅ Save the file securely
    safe_name = os.path.basename(document.filename)   # avoid any directory traversal
    filepath = os.path.join(UPLOAD_FOLDER, safe_name)

    try:
        with open(filepath, "wb") as f:
            f.write(await document.read())
    except Exception as e:
        return JSONResponse(content={"error": f"File save failed: {str(e)}"}, status_code=500)

    # ✅ Call LLM API
    try:
        answer = get_llm_response(query, filepath, DEFAULT_MODEL)
        return {"query": query, "answer": answer, "file": safe_name}
    except Exception as e:
        return JSONResponse(content={"error": f"LLM API failed: {str(e)}"}, status_code=500)