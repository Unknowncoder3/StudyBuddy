import requests
from bs4 import BeautifulSoup
import faiss
import numpy as np

from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

# ======================
# Model & Embeddings (UNCHANGED)
# ======================

llm = OllamaLLM(model="mistral")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ======================
# FAISS Vector Index (UNCHANGED)
# ======================

embedding_dim = 384
index = faiss.IndexFlatL2(embedding_dim)

# Maps FAISS row index -> {"url": ..., "text": ...}
vector_store = []

# ======================
# Utils: Scraping (LOGIC UNCHANGED)
# ======================

def scrape_website(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return f"Failed to fetch {url} (status code: {response.status_code})"

        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = " ".join(
            [p.get_text(separator=" ", strip=True) for p in paragraphs]
        )

        if not text.strip():
            return "No readable text content found on this page."

        return text[:5000]

    except Exception as e:
        return f"Error while scraping: {str(e)}"


# ======================
# Store in FAISS (LOGIC UNCHANGED)
# ======================

def store_in_faiss(text: str, url: str) -> str:
    global index, vector_store

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(text)

    if not chunks:
        return "Nothing to store (no chunks created)."

    chunk_vectors = embeddings.embed_documents(chunks)
    vectors = np.array(chunk_vectors, dtype=np.float32)

    if vectors.shape[1] != embedding_dim:
        return f"Embedding dimension mismatch: expected {embedding_dim}, got {vectors.shape[1]}"

    index.add(vectors)

    for chunk in chunks:
        vector_store.append({
            "url": url,
            "text": chunk
        })

    return f"Stored {len(chunks)} chunks from {url} in FAISS."


# ======================
# Retrieval + QA (LOGIC UNCHANGED)
# ======================

def retrieve_and_answer(query: str) -> str:
    global index, vector_store

    if index.ntotal == 0 or len(vector_store) == 0:
        return "No data stored yet. Please scrape a website first."

    query_vector = np.array(
        embeddings.embed_query(query),
        dtype=np.float32
    ).reshape(1, -1)

    if query_vector.shape[1] != embedding_dim:
        return "Query embedding dimension mismatch."

    k = min(5, index.ntotal)
    distances, indices = index.search(query_vector, k=k)

    context_chunks = []
    for idx in indices[0]:
        if 0 <= idx < len(vector_store):
            context_chunks.append(vector_store[idx]["text"])

    if not context_chunks:
        return "No relevant data found."

    context = "\n\n".join(context_chunks)

    prompt = (
        "You are a helpful assistant. Use ONLY the context below to answer the question.\n"
        "If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        "Answer:"
    )

    answer = llm.invoke(prompt)
    return answer if isinstance(answer, str) else str(answer)


# ======================
# PUBLIC API FUNCTIONS (FOR FLASK)
# ======================

def scrape_and_store(url: str):
    """
    Call this when a URL is submitted
    """
    text = scrape_website(url)

    if text.startswith("Failed") or text.startswith("Error") or text.startswith("No readable"):
        return {
            "status": "error",
            "message": text
        }

    store_msg = store_in_faiss(text, url)

    return {
        "status": "success",
        "store_message": store_msg,
        "preview": text[:1000]
    }


def ask_web_question(question: str) -> str:
    """
    Call this for Q&A
    """
    return retrieve_and_answer(question)
