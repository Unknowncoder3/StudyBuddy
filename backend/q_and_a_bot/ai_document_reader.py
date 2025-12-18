import faiss
import numpy as np
import PyPDF2

from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

# -----------------------------
# Global setup (UNCHANGED)
# -----------------------------

# Load AI Model (Ollama must be running)
llm = OllamaLLM(model="mistral")  # you can change to llama3 if needed

# Load Hugging Face Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# FAISS Index (L2 distance, dim=384)
EMBED_DIM = 384
index = faiss.IndexFlatL2(EMBED_DIM)

# Store chunks aligned with FAISS
chunk_store = []

# Store latest summary
summary_text = ""

# -----------------------------
# Helper functions (LOGIC UNCHANGED)
# -----------------------------

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file path
    """
    with open(file_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text


def store_in_faiss(text: str, filename: str) -> str:
    global index, chunk_store

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(text)

    if not chunks:
        return "No text chunks were created from this document."

    vectors = embeddings.embed_documents(chunks)
    vectors = np.array(vectors, dtype=np.float32)

    if vectors.shape[1] != EMBED_DIM:
        return f"Embedding dimension mismatch: expected {EMBED_DIM}, got {vectors.shape[1]}"

    index.add(vectors)

    for chunk in chunks:
        chunk_store.append({
            "filename": filename,
            "text": chunk
        })

    return f"Document stored successfully ({len(chunks)} chunks added)"


def generate_summary(text: str) -> str:
    global summary_text

    input_text = text[:3000]

    summary = llm.invoke(
        f"Summarize the following document in a concise and clear way:\n\n{input_text}"
    )

    summary_text = summary if isinstance(summary, str) else str(summary)
    return summary_text


def retrieve_and_answer(query: str) -> str:
    global index, chunk_store

    if index.ntotal == 0 or not chunk_store:
        return "No documents are stored yet. Please upload a PDF first."

    query_vector = embeddings.embed_query(query)
    query_vector = np.array(query_vector, dtype=np.float32).reshape(1, -1)

    D, I = index.search(query_vector, k=3)

    context_parts = []
    for idx in I[0]:
        if 0 <= idx < len(chunk_store):
            context_parts.append(chunk_store[idx]["text"])

    if not context_parts:
        return "No relevant data found in stored documents."

    context = "\n\n".join(context_parts)

    answer = llm.invoke(
        f"Based on the following document context, answer the user's question.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        f"Answer clearly and concisely:"
    )

    return answer if isinstance(answer, str) else str(answer)


# -----------------------------
# PUBLIC API FUNCTIONS (FOR FLASK)
# -----------------------------

def upload_pdf_and_process(file_path: str):
    """
    Call this once when a PDF is uploaded
    """
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        return {
            "status": "error",
            "message": "PDF contains no extractable text"
        }

    store_msg = store_in_faiss(text, file_path)
    summary = generate_summary(text)

    return {
        "status": "success",
        "store_message": store_msg,
        "summary": summary
    }


def ask_question(question: str) -> str:
    """
    Call this for Q&A
    """
    return retrieve_and_answer(question)
