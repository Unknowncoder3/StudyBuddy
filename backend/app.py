from flask import (
    Flask, request, jsonify,
    session, redirect, render_template, url_for
)
from flask_cors import CORS
from functools import wraps
import os, tempfile

# =========================
# IMPORT AI MODULES
# =========================
from code_analyzer.ai_based_code_analyzer import analyze_code_api as run_code_analysis
from ai_agent.ai_voice_assistant import voice_assistant_text_api
from q_and_a_bot.ai_document_reader import upload_pdf_and_process, ask_question
from video_analyzer.ai_based_video_analyzer import analyze_video
from webscrapper.ai_web_scrapper_faiss import scrape_and_store, ask_web_question

# =========================
# APP SETUP
# =========================
app = Flask(__name__)
app.secret_key = "studybuddy_secret_key"
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = tempfile.gettempdir()
users = {}  # demo user store

# =========================
# AUTH DECORATOR
# =========================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

# =========================
# PAGE ROUTES
# =========================
@app.route("/")
def root():
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

# =========================
# TOOL PAGES
# =========================
@app.route("/web")
@login_required
def web_page():
    return render_template("tools/web.html")

@app.route("/video")
@login_required
def video_page():
    return render_template("tools/video.html")


@app.route("/code")
@login_required
def code_page():
    return render_template("tools/code.html")

@app.route("/pdf")
@login_required
def pdf_page():
    return render_template("pdf.html")

@app.route("/voice")
@login_required
def voice_page():
    return render_template("tools/voice.html")


# =========================
# AUTH APIs
# =========================
@app.route("/api/register", methods=["POST"])
def register_api():
    data = request.json
    users[data["username"]] = data["password"]
    return jsonify({"message": "Registered"})

@app.route("/api/login", methods=["POST"])
def login_api():
    data = request.json
    if users.get(data["username"]) != data["password"]:
        return jsonify({"error": "Invalid credentials"}), 401
    session["user"] = data["username"]
    return jsonify({"message": "Login success"})

# =========================
# AI APIs
# =========================
@app.route("/analyze-code", methods=["POST"])
@login_required
def analyze_code_route():
    data = request.json

    code = data.get("code", "")
    language = data.get("language", "python")

    if not code.strip():
        return jsonify({"error": "Empty code"}), 400

    try:
        result = run_code_analysis(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/voice/ask", methods=["POST"])
@login_required
def voice_ask_api():
    data = request.json or {}
    query = data.get("text", "").strip()

    if not query:
        return jsonify({"error": "Empty input"}), 400

    try:
        response = voice_assistant_text_api(query)
        return jsonify({"response": response})
    except Exception as e:
        print("❌ Voice Assistant Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/pdf/upload", methods=["POST"])
@login_required
def pdf_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result = upload_pdf_and_process(path)
    return jsonify(result)

@app.route("/pdf/ask", methods=["POST"])
@login_required
def pdf_ask():
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = ask_question(question)
    return jsonify({"answer": answer})
@app.route("/document/upload", methods=["POST"])
@login_required
def document_upload_api():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result = upload_pdf_and_process(path)
    return jsonify(result)


@app.route("/document/ask", methods=["POST"])
@login_required
def document_ask_api():
    data = request.json
    question = data.get("question")
    return jsonify({"answer": ask_question(question)})

@app.route("/video/upload", methods=["POST"])
@login_required
def video_upload_api():
    if "file" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result = analyze_video(path)
    return jsonify(result)

@app.route("/web/scrape", methods=["POST"])
@login_required
def web_scrape_api():
    url = request.json.get("url")
    return jsonify(scrape_and_store(url))

@app.route("/web/ask", methods=["POST"])
@login_required
def web_ask_api():
    question = request.json.get("question")
    return jsonify({"answer": ask_web_question(question)})

@app.route("/api/web/ask", methods=["POST"])
@login_required
def web_ask():
    return jsonify({"answer": ask_web_question(request.json["question"])})
@app.route("/voice/ask", methods=["POST"])
@login_required
def voice_assistant_api():
    text = request.json.get("text")
    response = voice_assistant_text_api(text)
    return jsonify({"response": response})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
