from flask import Flask, render_template
from routes import api  # Register the Blueprint from routes.py
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key"  # Replace with a secure key in production

# Register Blueprint
app.register_blueprint(api)

# Ensure upload folder exists
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Home route (UI)
@app.route("/")
def home():
    return render_template("index.html")

# Run with correct host/port (Render-compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
