from flask import Flask, request, jsonify, render_template
import os
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

app = Flask(__name__)

# Ensure folders exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("vectors", exist_ok=True)

# Load model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# FAISS index setup
embedding_dim = 384
index_path = "vectors/faiss_index.index"
texts_path = "vectors/doc_texts.pkl"

if os.path.exists(index_path) and os.path.exists(texts_path):
    index = faiss.read_index(index_path)
    with open(texts_path, "rb") as f:
        doc_texts = pickle.load(f)
else:
    index = faiss.IndexFlatL2(embedding_dim)
    doc_texts = []

# ---------------- Upload PDF ----------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    # Extract text from PDF
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    # Split text into sentences
    sentences = [s.strip() for s in text.split("\n") if s.strip() != ""]

    # Generate embeddings and update FAISS index
    embeddings = model.encode(sentences)
    index.add(np.array(embeddings, dtype="float32"))
    doc_texts.extend(sentences)

    # Save index & texts
    faiss.write_index(index, index_path)
    with open(texts_path, "wb") as f:
        pickle.dump(doc_texts, f)

    return jsonify({"message": f"{file.filename} uploaded and indexed successfully!"})

# ---------------- Ask Question ----------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    if question == "":
        return jsonify({"answer": "Please provide a question."})

    # Generate embedding for question
    q_embedding = model.encode([question])
    D, I = index.search(np.array(q_embedding, dtype="float32"), k=3)

    # Return relevant sentences
    answers = [doc_texts[i] for i in I[0]]
    return jsonify({"answer": " ".join(answers)})

# ---------------- Home Page ----------------
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
