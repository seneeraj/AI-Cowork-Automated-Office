import os
import streamlit as st

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

try:
    import faiss
    USE_FAISS = True
except:
    USE_FAISS = False

from core.skill_engine import SkillEngine
from core.executor import Executor
from services.llm import generate_response
from core.knowledge_engine import KnowledgeEngine



class Agent:
    def __init__(self):
        self.skill_engine = SkillEngine()
        self.executor = Executor()
        self.knowledge_engine = KnowledgeEngine()
        self.knowledge_engine.build_index()

    # -----------------------------
    # MAIN PROCESS FUNCTION
    # -----------------------------
    def process(self, user_input, file_text=None, memory=None):

        # -----------------------------
        # 1. TRY SKILL EXECUTION (TASK MODE)
        # -----------------------------
        try:
            skill = self.skill_engine.match_skill(user_input)
        except:
            skill = None

        if skill:
            try:
                results = self.executor.run_steps(skill["steps"], user_input)
                combined_results = "\n".join(results)
            except:
                combined_results = "Task execution failed."

            final_prompt = f"""
You are generating a FINAL structured business output.

Based on these results:
{combined_results}

Return in this format:

Summary:
- Short summary

Steps:
1. Step one
2. Step two

Recommendation:
- Clear action
"""

            response = generate_response(final_prompt)

            return {
                "mode": "task",
                "response": response
            }

        # -----------------------------
        # 2. CHAT MODE (RAG + MEMORY)
        # -----------------------------

        # Conversation memory
        conversation_context = ""
        if memory:
            try:
                history = memory.get_messages(memory.get_chats()[0])
                conversation_context = "\n".join(
                    [f"{m['role']}: {m['content']}" for m in history[-3:]]
                )
            except:
                conversation_context = ""

        # Knowledge retrieval (RAG)
        try:
            knowledge_context = self.knowledge_engine.search(user_input)
        except:
            knowledge_context = ""

        # File context (optional)
        file_context = file_text[:1500] if file_text else ""

        # -----------------------------
        # FINAL PROMPT
        # -----------------------------
        final_prompt = f"""
You are an intelligent AI assistant.

Use available context to answer the user.

---------------------
KNOWLEDGE:
{knowledge_context}

---------------------
CONVERSATION:
{conversation_context}

---------------------
DOCUMENT:
{file_context}

---------------------
USER QUESTION:
{user_input}

---------------------

Instructions:
- If knowledge is relevant → use it
- If not → answer normally
- Be clear and structured
- Avoid generic answers
"""

        response = generate_response(final_prompt)

        return {
            "mode": "chat",
            "response": response
        }