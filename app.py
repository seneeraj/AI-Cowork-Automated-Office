import streamlit as st
import os
from datetime import datetime, timedelta

from core.agent import Agent
from core.memory import Memory

st.set_page_config(page_title="AI Cowork Automated Office", layout="wide")

st.title("AI Cowork Automated Office")
st.caption("Automated office System for MSME, Remote Professionals and Freelancers")

BASE_DIR = os.path.dirname(__file__)
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# =========================================================
# INIT
# =========================================================
if "memory" not in st.session_state:
    st.session_state.memory = Memory()

if "agent" not in st.session_state:
    st.session_state.agent = Agent()

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "popup" not in st.session_state:
    st.session_state.popup = None

memory = st.session_state.memory
agent = st.session_state.agent

# =========================================================
# CHAT INIT
# =========================================================
chat_titles = memory.get_chat_titles()

if not chat_titles:
    st.session_state.current_chat = memory.create_chat()
elif st.session_state.current_chat is None:
    st.session_state.current_chat = chat_titles[0][0]

# =========================================================
# NAVIGATION
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "💬 Chat", "⚡ Actions", "📁 Knowledge", "🏢 Booking"],
    index=["🏠 Dashboard", "💬 Chat", "⚡ Actions", "📁 Knowledge", "🏢 Booking"].index(st.session_state.page)
)

st.session_state.page = page

# =========================================================
# HELPERS
# =========================================================
def detect_intent(text):
    text = text.lower()
    if "email" in text: return "email"
    if "report" in text: return "report"
    if "analyze" in text: return "analysis"
    return None

def get_upcoming_bookings(bookings):
    now = datetime.now()
    upcoming = []

    for b in bookings:
        try:
            date_str = b[1]
            time_range = b[2].replace("–", "-")

            start_str, end_str = [t.strip() for t in time_range.split("-")]

            end_dt = datetime.strptime(
                f"{date_str} {end_str}",
                "%Y-%m-%d %I:%M %p"
            )

            if end_dt >= now:
                upcoming.append(b)
        except:
            continue

    return sorted(
        upcoming,
        key=lambda x: datetime.strptime(
            f"{x[1]} {x[2].split('-')[0].strip()}",
            "%Y-%m-%d %I:%M %p"
        )
    )

# =========================================================
# WORKFLOW
# =========================================================
def handle_workflow(user_input):
    wf = st.session_state.get("workflow")

    if not wf:
        return None

    if wf["type"] == "email":

        if wf["step"] == "ask_to":
            wf["data"]["to"] = user_input
            wf["step"] = "ask_subject"
            return "What is the subject?"

        elif wf["step"] == "ask_subject":
            wf["data"]["subject"] = user_input
            wf["step"] = "ask_purpose"
            return "What is the purpose?"

        elif wf["step"] == "ask_purpose":
            wf["data"]["purpose"] = user_input
            data = wf["data"]
            st.session_state.workflow = None

            knowledge = agent.knowledge_engine.search(
                data["subject"] + " " + data["purpose"]
            )

            prompt = f"""
Use company knowledge to write email.

{knowledge}

To: {data['to']}
Subject: {data['subject']}
Purpose: {data['purpose']}
"""

            result = agent.process(prompt)

            memory.save_activity(st.session_state.current_chat, "📧 Email generated")

            return result.get("response", "")

    elif wf["type"] == "report":
        st.session_state.workflow = None
        result = agent.process(f"Generate report on {user_input}")

        memory.save_activity(st.session_state.current_chat, "📄 Report generated")

        return result.get("response", "")

    elif wf["type"] == "analysis":
        st.session_state.workflow = None
        result = agent.process(f"Analyze:\n{user_input}")

        memory.save_activity(st.session_state.current_chat, "📊 Data analyzed")

        return result.get("response", "")

    return None

# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":

    st.title("🏠 Dashboard")

    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)

    if col1.button("📧 Write Email"):
        st.session_state.page = "💬 Chat"

    if col2.button("📄 Generate Report"):
        st.session_state.page = "💬 Chat"

    if col3.button("📊 Analyze Data"):
        st.session_state.page = "💬 Chat"

    # Activity
    st.subheader("🕒 Recent Activity")
    activities = memory.get_activities(st.session_state.current_chat)

    if activities:
        for act in activities:
            st.write(f"• {act}")
    else:
        st.info("No recent activity")

    # Usage
    st.subheader("⚡ Usage Summary")
    messages = memory.get_messages(st.session_state.current_chat)

    email_count = sum("email" in m["content"].lower() for m in messages if m["role"]=="assistant")
    report_count = sum("report" in m["content"].lower() for m in messages if m["role"]=="assistant")
    analysis_count = sum("analy" in m["content"].lower() for m in messages if m["role"]=="assistant")

    col1, col2, col3 = st.columns(3)
    col1.metric("Emails", email_count)
    col2.metric("Reports", report_count)
    col3.metric("Analysis", analysis_count)

    # Booking summary
    st.subheader("🏢 Upcoming Bookings")

    bookings = memory.get_bookings(st.session_state.current_chat)
    upcoming = get_upcoming_bookings(bookings)

    if upcoming:
        for b in upcoming:
            st.write(f"🟢 {b[0]} | {b[1]} | {b[2]}")
    else:
        st.info("No upcoming bookings")

# =========================================================
# CHAT
# =========================================================
elif page == "💬 Chat":

    st.title("💬 Chat")

    messages = memory.get_messages(st.session_state.current_chat)

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    uploaded_file = st.file_uploader(
    "📂 Upload data file for analysis",
    type=["csv", "xlsx", "txt"]
)

    import pandas as pd

    file_content = None

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                file_content = df.head(50).to_string()

            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                file_content = df.head(50).to_string()

            elif uploaded_file.name.endswith(".txt"):
                file_content = uploaded_file.read().decode("utf-8")

            st.success("File loaded successfully")

        except Exception as e:
            st.error(f"Error reading file: {e}")

    user_input = st.chat_input("Ask anything...")

    if user_input:
        memory.save_message(st.session_state.current_chat, "user", user_input)

        if st.session_state.workflow:
            response = handle_workflow(user_input)
        else:
            intent = detect_intent(user_input)

            if intent == "email":
                st.session_state.workflow = {"type": "email", "step": "ask_to", "data": {}}
                response = "Who is the recipient?"
            elif intent == "report":
                st.session_state.workflow = {"type": "report"}
                response = "What topic?"
            elif intent == "analysis":
                st.session_state.workflow = {"type": "analysis"}
                response = "Provide data"
            else:
                if file_content:
                    prompt = f"""
                Analyze the following data:

                {file_content}

                User Question:
                {user_input}
                """
                    result = agent.process(prompt)
                else:
                    result = agent.process(user_input, memory=memory)           
                
                
                response = result.get("response", "")

        memory.save_message(st.session_state.current_chat, "assistant", response)
        st.rerun()

# =========================================================
# ACTIONS
# =========================================================
elif page == "⚡ Actions":

    st.title("⚡ AI Tools Hub")

    tool = st.selectbox(
        "Select Tool",
        [
            "📧 Bulk Email Sender",
            "📱 WhatsApp Message Sender",
            "🌍 Translator",
            "📄 Office Templates",
            "💼 LinkedIn Post Generator",
            "🔗 URL Summarizer"
        ]
    )

    # =========================================================
    # BULK EMAIL
    # =========================================================
    if tool == "📧 Bulk Email Sender":

        st.subheader("📧 Bulk Email")

        emails = st.text_area("Enter Emails (comma separated)")
        subject = st.text_input("Subject")
        message = st.text_area("Message")

        if st.button("Send Emails"):

            prompt = f"""
Write a professional bulk email.

Subject: {subject}
Message: {message}
Recipients: {emails}
"""

            result = agent.process(prompt)

            st.success("Emails Prepared (Integrate SMTP to send)")
            st.write(result.get("response", ""))

            memory.save_activity(
                st.session_state.current_chat,
                "📧 Bulk email prepared"
            )

    # =========================================================
    # WHATSAPP
    # =========================================================
    elif tool == "📱 WhatsApp Message Sender":

        st.subheader("📱 WhatsApp Messages")

        numbers = st.text_area("Phone Numbers")
        message = st.text_area("Message")

        if st.button("Send WhatsApp Messages"):

            prompt = f"""
Write a short WhatsApp message:

{message}
"""

            result = agent.process(prompt)

            st.success("Message Ready (Integrate WhatsApp API)")
            st.write(result.get("response", ""))

            memory.save_activity(
                st.session_state.current_chat,
                "📱 WhatsApp campaign created"
            )

    # =========================================================
    # TRANSLATOR
    # =========================================================
    elif tool == "🌍 Translator":

        st.subheader("🌍 Translate Text")

        text = st.text_area("Enter text")
        lang = st.selectbox("Select Language", ["Hindi", "French", "Spanish", "German"])

        if st.button("Translate"):

            result = agent.process(f"Translate to {lang}: {text}")

            st.success("Translated")
            st.write(result.get("response", ""))

            memory.save_activity(
                st.session_state.current_chat,
                f"🌍 Translated to {lang}"
            )

    # =========================================================
    # TEMPLATES
    # =========================================================
    elif tool == "📄 Office Templates":

        st.subheader("📄 Template Generator")

        template_type = st.selectbox(
            "Template Type",
            ["Business Proposal", "Leave Application", "Invoice", "Meeting Notes"]
        )

        if st.button("Generate Template"):

            result = agent.process(f"Create {template_type} template")

            st.write(result.get("response", ""))

            memory.save_activity(
                st.session_state.current_chat,
                f"📄 Template created ({template_type})"
            )

    # =========================================================
    # LINKEDIN POST
    # =========================================================
    elif tool == "💼 LinkedIn Post Generator":

        st.subheader("💼 LinkedIn Content")

        topic = st.text_input("Enter Topic")

        if st.button("Generate Post"):

            result = agent.process(f"Write a professional LinkedIn post on {topic}")

            st.write(result.get("response", ""))

            memory.save_activity(
                st.session_state.current_chat,
                "💼 LinkedIn post created"
            )

    # =========================================================
    # URL SUMMARIZER
    # =========================================================
    elif tool == "🔗 URL Summarizer":

        st.subheader("🔗 Summarize URL")

        url = st.text_input("Enter URL")

        if st.button("Summarize"):

            result = agent.process(f"Summarize content from: {url}")

            st.write(result.get("response", ""))

            memory.save_activity(
                st.session_state.current_chat,
                "🔗 URL summarized"
            )

# =========================================================
# KNOWLEDGE
# =========================================================
elif page == "📁 Knowledge":

    st.title("📁 Knowledge Base")
    os.makedirs("knowledge", exist_ok=True)

    file = st.file_uploader("Upload Your Organization's Knwoledge Database", type=["txt"])

    if file:
        file_path = os.path.join(KNOWLEDGE_DIR,st.session_state.edit_file )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file.read().decode("utf-8"))

    agent.knowledge_engine.build_index()
        st.success("Uploaded")

    files = os.listdir("KNOWLEDGE_DIR")

    # session state for editing
    if "edit_file" not in st.session_state:
        st.session_state.edit_file = None

    for f in files:

        col1, col2, col3 = st.columns([6,1,1])

        col1.write(f)

        # ✏️ EDIT BUTTON
        if col2.button("✏️", key=f"edit_{f}"):
            st.session_state.edit_file = f

        # 🗑 DELETE BUTTON
        if col3.button("🗑", key=f"del_{f}"):
            os.remove(os.path.join("KNOWLEDGE_DIR", f))
            agent.knowledge_engine.build_index()
            st.rerun()


    # =========================================================
# FILE EDITOR
# =========================================================
if st.session_state.edit_file:

    file_path = os.path.join("knowledge", st.session_state.edit_file)

    st.markdown(f"### ✏️ Editing: {st.session_state.edit_file}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        content = ""

    new_content = st.text_area(
        "Edit content",
        value=content,
        height=300
    )

    col1, col2 = st.columns(2)

    # 💾 SAVE
    if col1.button("💾 Save Changes"):

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        agent.knowledge_engine.build_index()

        st.success("File updated successfully")

        st.session_state.edit_file = None
        st.rerun()

    # ❌ CANCEL
    if col2.button("❌ Cancel"):
        st.session_state.edit_file = None
        st.rerun()





# =========================================================
# BOOKING
# =========================================================
elif page == "🏢 Booking":

    st.title("🏢 Booking System")

    def generate_slots():
        slots = []
        start = datetime.strptime("09:00", "%H:%M")
        end = datetime.strptime("17:00", "%H:%M")

        while start < end:
            slots.append(start.strftime("%I:%M %p"))
            start += timedelta(minutes=15)

        return slots

    slots = generate_slots()

    space = st.selectbox("Space", ["Conference Room", "Desk", "Flexible Seat", "Recreation Hall"])
    date = st.date_input("Date")
    selected = st.multiselect("Time Slots", slots)

    if st.button("Confirm Booking"):

        if selected:
            s = sorted(selected, key=lambda x: datetime.strptime(x, "%I:%M %p"))
            start_time = s[0]
            end_time = (datetime.strptime(s[-1], "%I:%M %p") + timedelta(minutes=15)).strftime("%I:%M %p")

            memory.save_booking(
                st.session_state.current_chat,
                space,
                str(date),
                f"{start_time} - {end_time}"
            )

            memory.save_activity(
                st.session_state.current_chat,
                f"📅 Booking created ({space})"
            )

            st.success(f"{start_time} → {end_time}")

    # Booking list
    st.markdown("### 📅 Upcoming Bookings")

    bookings = memory.get_bookings(st.session_state.current_chat)
    upcoming = get_upcoming_bookings(bookings)

    if upcoming:
        for b in upcoming:
            col1, col2 = st.columns([6,1])

            col1.write(f"🟢 {b[0]} | {b[1]} | {b[2]}")

            if col2.button("❌", key=f"del_{b}"):
                memory.delete_booking(st.session_state.current_chat, b[0], b[1], b[2])

                memory.save_activity(
                    st.session_state.current_chat,
                    f"❌ Booking cancelled ({b[0]})"
                )

                st.rerun()
    else:
        st.info("No upcoming bookings")