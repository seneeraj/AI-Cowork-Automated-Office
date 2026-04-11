import streamlit as st

from core.skill_engine import SkillEngine
from core.executor import Executor
from services.llm import generate_response
from core.knowledge_engine import KnowledgeEngine


class Agent:
    def __init__(self):
        self.skill_engine = SkillEngine()
        self.executor = Executor()
        self.knowledge_engine = KnowledgeEngine()

        # Build knowledge index safely
        try:
            self.knowledge_engine.build_index()
        except:
            pass

    # =========================================================
    # MAIN PROCESS FUNCTION
    # =========================================================
    def process(self, user_input, file_text=None, memory=None):

        # =====================================================
        # 1. TASK MODE (SKILL EXECUTION)
        # =====================================================
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
You are generating a structured business output.

Results:
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

        # =====================================================
        # 2. CHAT MODE (RAG + MEMORY)
        # =====================================================

        # -----------------------------
        # Conversation Memory (FIXED)
        # -----------------------------
        conversation_context = ""

        if memory:
            try:
                chat_id = st.session_state.get("current_chat")

                if chat_id:
                    history = memory.get_messages(chat_id)

                    last_msgs = history[-3:] if len(history) > 3 else history

                    conversation_context = "\n".join(
                        [f"{m['role']}: {m['content']}" for m in last_msgs]
                    )
            except:
                conversation_context = ""

        # -----------------------------
        # Knowledge Retrieval (LIGHT RAG)
        # -----------------------------
        try:
            knowledge_context = self.knowledge_engine.search(user_input)
        except:
            knowledge_context = ""

        # -----------------------------
        # File Context (SAFE)
        # -----------------------------
        file_context = file_text[:1500] if file_text else ""

        # =====================================================
        # FINAL PROMPT
        # =====================================================
        final_prompt = f"""
You are an intelligent AI assistant for business productivity.

Use available context carefully.

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
- Use knowledge if relevant
- Use document if provided
- Use conversation context if needed
- Otherwise answer normally
- Be clear, structured, and practical
"""

        response = generate_response(final_prompt)

        return {
            "mode": "chat",
            "response": response
        }
