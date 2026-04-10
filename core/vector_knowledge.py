import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Safe FAISS import
try:
    import faiss
    FAISS_AVAILABLE = True
except:
    FAISS_AVAILABLE = False


class VectorKnowledgeBase:
    def __init__(self, folder="knowledge"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.texts = []
        self.index = None
        self.embeddings = None

        self.load_data(folder)

    # -----------------------------
    # LOAD DATA
    # -----------------------------
    def load_data(self, folder):
        chunks = []

        if os.path.exists(folder):
            for file in os.listdir(folder):
                with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                    text = f.read()
                    chunks.extend(self.chunk_text(text))

        self.texts = chunks

        if chunks:
            embeddings = self.model.encode(chunks)

            if FAISS_AVAILABLE:
                dim = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dim)
                self.index.add(np.array(embeddings))
            else:
                self.embeddings = embeddings  # fallback

    # -----------------------------
    # TEXT CHUNKING
    # -----------------------------
    def chunk_text(self, text, chunk_size=300):
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    # -----------------------------
    # SEARCH
    # -----------------------------
    def search(self, query, k=3):
        if not self.texts:
            return ""

        query_vec = self.model.encode([query])

        if FAISS_AVAILABLE and self.index:
            distances, indices = self.index.search(np.array(query_vec), k)
            results = [self.texts[i] for i in indices[0]]
        else:
            # fallback (cosine similarity)
            similarities = np.dot(self.embeddings, query_vec.T).flatten()
            top_k = similarities.argsort()[-k:][::-1]
            results = [self.texts[i] for i in top_k]

        return "\n\n".join(results)