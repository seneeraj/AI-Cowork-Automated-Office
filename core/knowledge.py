import os

class KnowledgeBase:
    def __init__(self, folder="knowledge"):
        self.data = self.load_files(folder)

    def load_files(self, folder):
        content = ""
        if os.path.exists(folder):
            for file in os.listdir(folder):
                with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                    content += f.read() + "\n"
        return content

    def get_context(self):
        return self.data[:3000]  # limit size