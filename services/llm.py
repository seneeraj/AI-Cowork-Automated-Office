from openai import OpenAI
import streamlit as st

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# -----------------------------
# INTENT DETECTION
# -----------------------------
def detect_intent(prompt: str) -> str:
    prompt_lower = prompt.lower()

    generate_keywords = ["write", "create", "generate", "draft", "email", "report"]
    analyze_keywords = ["analyze", "insight", "trend", "evaluate"]

    if any(k in prompt_lower for k in generate_keywords):
        return "generate"
    elif any(k in prompt_lower for k in analyze_keywords):
        return "analyze"
    else:
        return "explain"

# -----------------------------
# SYSTEM PROMPTS
# -----------------------------
def get_system_prompt(intent: str) -> str:

    return f"""
You are an intelligent AI assistant.

Your job:
- Understand user intent
- Decide if enough information is available

RULES:

1. If information is COMPLETE:
→ Give final answer

2. If information is INCOMPLETE:
→ Ask follow-up questions
→ Be specific and minimal

3. Never assume missing details

4. Be conversational and natural

5. For generation tasks:
→ Ask for missing fields like:
   - recipient
   - subject
   - purpose

6. For analysis:
→ Ask for data clarity if needed

IMPORTANT:
- Do NOT give steps unless asked
- Do NOT hallucinate missing info
"""

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_response(prompt: str, context: str = ""):

    try:
        intent = detect_intent(prompt)
        system_prompt = get_system_prompt(intent)

        full_prompt = f"""
Conversation Context:
{context}

User Query:
{prompt}
"""

        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ ERROR: {str(e)}"