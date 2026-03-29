"""
StudySync - PDF Merge & Topic Analysis Backend
============================================
Run karne ke liye:
  pip install flask pdfplumber PyPDF2 reportlab scikit-learn nltk python-docx flask-cors
  python app.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from pathlib import Path

from pdf_processor import PDFProcessor
from topic_analyzer import TopicAnalyzer
from note_generator import NoteGenerator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

processor = PDFProcessor()
analyzer  = TopicAnalyzer()
generator = NoteGenerator()


# ───────────────────────────────────────────────────────────────
# 1. PDF Upload Route
# ───────────────────────────────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Multiple PDFs ek saath upload karein."""
    if "files" not in request.files:
        return jsonify({"error": "Koi file nahi mili"}), 400

    saved = []
    for f in request.files.getlist("files"):
        if f.filename.endswith((".pdf", ".docx", ".txt")):
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            saved.append({"name": f.filename, "path": path})

    return jsonify({"uploaded": saved, "count": len(saved)})


# ───────────────────────────────────────────────────────────────
# 2. Analyze Topics
# ───────────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    """Uploaded PDFs se topics extract karein."""
    data = request.json or {}
    filenames = data.get("files", [])

    all_texts = {}
    for name in filenames:
        path = os.path.join(UPLOAD_FOLDER, name)
        if os.path.exists(path):
            all_texts[name] = processor.extract_text(path)

    if not all_texts:
        return jsonify({"error": "Koi valid file nahi mili"}), 400

    topics = analyzer.find_common_topics(all_texts)
    return jsonify({"topics": topics, "total": len(topics)})


# ───────────────────────────────────────────────────────────────
# 3. Merge + Generate Notes (PDF/TXT)
# ───────────────────────────────────────────────────────────────
@app.route("/merge", methods=["POST"])
def merge():
    """Common topics ko ek note me merge karein."""
    data = request.json or {}
    filenames = data.get("files", [])
    fmt = data.get("format", "pdf")   # "pdf" | "txt"

    all_texts = {}
    for name in filenames:
        path = os.path.join(UPLOAD_FOLDER, name)
        if os.path.exists(path):
            all_texts[name] = processor.extract_text(path)

    topics = analyzer.find_common_topics(all_texts)

    outpath = os.path.join(OUTPUT_FOLDER, f"merged_notes.{fmt}")
    generator.generate(topics, outpath, fmt=fmt)

    return jsonify({"output": outpath, "topics_merged": len(topics)})


# ───────────────────────────────────────────────────────────────
# 4. File Download
# ───────────────────────────────────────────────────────────────
@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File nahi mili"}), 404
    return send_file(path, as_attachment=True)


# ───────────────────────────────────────────────────────────────
# Server Start
# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("StudySync server chal raha hai → http://localhost:5000")
    app.run(debug=True, port=5000)
