from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

import os
from werkzeug.utils import secure_filename

from chatbot import get_response
from database import create_database, save_message, get_history
from memory import create_memory
from auth import create_users_table, register_user, login_user
from file_processor import process_file


# =====================================
# Flask Configuration
# =====================================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "change_this_secret_key")


# =====================================
# Upload Configuration
# =====================================

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "txt",
    "docx"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================
# Database Initialization
# =====================================

create_database()
create_memory()
create_users_table()


# =====================================
# Helper Functions
# =====================================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def is_logged_in():
    return "user_id" in session or "guest" in session


# =====================================
# Home
# =====================================

@app.route("/")
def home():

    if not is_logged_in():
        return redirect("/login")

    return render_template(
        "index.html",
        username=session.get("username", "Guest")
    )


# =====================================
# Register
# =====================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            return "All fields are required", 400

        if register_user(username, email, password):
            return redirect("/login")

        return "Username or email already exists", 409

    return render_template("register.html")


# =====================================
# Login
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = login_user(email, password)

        if user:

            session.clear()

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/")

        return "Invalid email or password", 401

    return render_template("login.html")


# =====================================
# Guest Mode
# =====================================

@app.route("/guest")
def guest():

    session.clear()

    session["guest"] = True
    session["username"] = "Guest"

    return redirect("/")


# =====================================
# Logout
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =====================================
# Chat API
# =====================================

@app.route("/chat", methods=["POST"])
def chat():

    if not is_logged_in():
        return jsonify(
            {"reply": "Please login first"}
        ), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify(
            {"reply": "No message received"}
        ), 400

    message = data.get("message", "").strip()

    if not message:
        return jsonify(
            {"reply": "Please enter a message"}
        ), 400

    user_id = 0 if "guest" in session else session["user_id"]

    try:

        reply = get_response(user_id, message)

        if "guest" not in session:
            save_message(user_id, message, reply)

        return jsonify(
            {"reply": reply}
        )

    except Exception as e:

        print("Chat Error:", e)

        return jsonify(
            {"reply": "Something went wrong. Please try again."}
        ), 500


# =====================================
# Chat History
# =====================================

@app.route("/history")
def history():

    if "guest" in session:
        return jsonify({"history": []})

    if "user_id" not in session:
        return redirect("/login")

    chats = get_history(session["user_id"])

    return jsonify({"history": chats})


# =====================================
# File Upload
# =====================================

@app.route("/upload", methods=["POST"])
def upload_file():

    if not is_logged_in():
        return jsonify(
            {
                "success": False,
                "message": "Please login first."
            }
        ), 401

    if "file" not in request.files:
        return jsonify(
            {
                "success": False,
                "message": "No file selected."
            }
        ), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify(
            {
                "success": False,
                "message": "No file selected."
            }
        ), 400

    if not allowed_file(file.filename):
        return jsonify(
            {
                "success": False,
                "message": "Unsupported file type."
            }
        ), 400

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    try:

        process_file(filepath)

        return jsonify(
            {
                "success": True,
                "message": "File processed successfully."
            }
        )

    except Exception as e:

        print("Upload Error:", e)

        return jsonify(
            {
                "success": False,
                "message": "File processing failed."
            }
        ), 500


# =====================================
# Global Error Handlers
# =====================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {
                "success": False,
                "message": "Internal Server Error"
            }
        ),
        500,
    )


# =====================================
# Run Server
# =====================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function