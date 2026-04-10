from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

class VectorKnowledgeBase:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = []
        self.embeddings = []

        self.build_index()

    def build_index(self):

        folder = "knowledge"

        if not os.path.exists(folder):
            return

        self.documents = []
        texts = []

        for file in os.listdir(folder):
            path = os.path.join(folder, file)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                self.documents.append(content)
                texts.append(content)

        if texts:
            self.embeddings = self.model.encode(texts)

    def search(self, query, top_k=2):

        if not self.documents:
            return ""

        query_vec = self.model.encode([query])

        scores = cosine_similarity(query_vec, self.embeddings)[0]

        top_indices = np.argsort(scores)[-top_k:]

        return "\n\n".join([self.documents[i] for i in top_indices])
