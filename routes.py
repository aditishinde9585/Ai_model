from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from llm_handler import get_llm_response
import os

api = Blueprint('api', __name__)
UPLOAD_FOLDER = 'uploads/'
DEFAULT_MODEL = "mistralai/mistral-7b-instruct"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@api.route('/api/query', methods=['POST'])
def api_query():
    query = request.form.get('query')
    file = request.files.get('document')

    # Handle file upload (optional on next queries)
    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        session['file_path'] = filepath
        session['file_name'] = filename
    else:
        filepath = session.get('file_path')

    if not filepath:
        return jsonify({"error": "No file uploaded"}), 400

    # Get LLM response
    answer = get_llm_response(query, filepath, DEFAULT_MODEL)
    return jsonify({
        "query": query,
        "answer": answer,
        "file": session.get('file_name')
    })