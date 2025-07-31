from flask import Flask, render_template
from routes import api  # make sure your Blueprint is named api in routes.py
import os

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"
app.register_blueprint(api)  # Register the API routes

if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)