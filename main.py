from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from llm_handler import get_llm_response

app = Flask(__name__)
app.secret_key = "your_secret_key"
UPLOAD_FOLDER = "uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

chat_history = []
users = {}  # Simple in-memory store for demo purposes

@app.route("/", methods=["GET"])
def home():
    if not session.get("logged_in"):
        return redirect(url_for("auth"))
    return render_template("index.html", history=chat_history)

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    if not session.get("logged_in"):
        return redirect(url_for("auth"))

    file = request.files.get("document")
    query = request.form.get("query")
    if not file or not query:
        return jsonify({"error": "File and query required."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    response = get_llm_response(query, filepath)
    chat_history.append({"role": "user", "content": query})
    chat_history.append({"role": "assistant", "content": response})

    return jsonify({"query": query, "response": response})

@app.route("/chat", methods=["GET"])
def redirect_to_home():
    return redirect("/")

@app.route("/clear", methods=["POST"])
def clear_chat():
    global chat_history
    chat_history = []
    return redirect("/")

@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "GET":
        return render_template("login.html")

    mode = request.form.get("mode")
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return render_template("login.html", error="Email and password required.")

    if mode == "signup":
        if email in users:
            return render_template("login.html", error="User already exists.")
        users[email] = password
        session["logged_in"] = True
        return redirect(url_for("home"))

    elif mode == "login":
        if users.get(email) == password:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials.")

    return render_template("login.html", error="Invalid mode.")

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("auth"))

if __name__ == "__main__":
    app.run(debug=True)