import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class KnowledgeEngine:
    def __init__(self, folder="knowledge"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Storage
        self.text_chunks = []
        self.index = None

        # Build index
        self.build_index()

    # -----------------------------
    # LOAD FILES
    # -----------------------------
    def load_documents(self):
        docs = []

        for file in os.listdir(self.folder):
            path = os.path.join(self.folder, file)

            if os.path.isfile(path) and file.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    docs.append(f.read())

        return docs

    # -----------------------------
    # SPLIT INTO CHUNKS
    # -----------------------------
    def split_chunks(self, text, chunk_size=300):
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    # -----------------------------
    # BUILD FAISS INDEX
    # -----------------------------
    def build_index(self):
        docs = self.load_documents()

        self.text_chunks = []

        for doc in docs:
            chunks = self.split_chunks(doc)
            self.text_chunks.extend(chunks)

        if not self.text_chunks:
            self.index = None
            return

        embeddings = self.model.encode(self.text_chunks)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings))

    # -----------------------------
    # SEARCH
    # -----------------------------
    def search(self, query, top_k=3):
        if self.index is None:
            return ""

        query_embedding = self.model.encode([query])

        distances, indices = self.index.search(
            np.array(query_embedding),
            top_k
        )

        results = []

        for idx in indices[0]:
            if idx < len(self.text_chunks):
                results.append(self.text_chunks[idx])

        return "\n\n".join(results)