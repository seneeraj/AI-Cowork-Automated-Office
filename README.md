# AI-Cowork-Automated-Office

### *Office Automation System for Small Businesses, MSME, Remote Professionals, Freelancers*

---

## 📌 Overview

**AI-Cowork-Automated-Office** is an intelligent office automation platform designed for small businesses to streamline daily operations using AI.

It combines:

* 💬 Conversational AI (Chat-based workflows)
* 📧 Email automation
* 📊 Data analysis
* 📄 Report generation
* 📱 WhatsApp & communication tools
* 📁 Knowledge-based AI (RAG system)
* 🏢 Booking management system

---

## 🎯 Key Features

### 💬 AI Chat Assistant

* Conversational interface like ChatGPT
* Auto-detects user intent (Email, Report, Analysis)
* Multi-step workflow automation

---

### ⚡ AI Tools Hub (Actions)

* 📧 Bulk Email Generator & Sender
* 📱 WhatsApp Messaging (via Twilio)
* 🌍 Language Translator
* 📄 Office Template Generator
* 💼 LinkedIn Post Creator
* 🔗 URL Summarizer

---

### 📁 Knowledge Base (RAG System)

* Upload `.txt` company documents
* Edit / Delete knowledge files
* AI uses internal knowledge for responses

---

### 📊 Data Analysis

* Upload CSV / Excel files
* AI-driven insights and summaries

---

### 🏢 Booking System

* 15-minute slot-based booking
* Continuous slot selection
* Upcoming bookings view
* Cancel bookings

---

### 🏠 Dashboard

* Quick Actions
* Recent Activity tracking
* Usage statistics
* Upcoming bookings summary

---

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit
* **AI/LLM:** OpenAI API
* **RAG System:** FAISS + Sentence Transformers
* **Database:** SQLite
* **Data Processing:** Pandas, NumPy
* **Communication APIs:** Twilio (WhatsApp), SMTP (Email)

---

## 📂 Project Structure

```
clarity-ai/
│
├── app.py
├── requirements.txt
├── data.db
│
├── core/
│   ├── agent.py
│   ├── memory.py
│
├── services/
│   ├── communication.py
│
├── knowledge/
│
└── .streamlit/
    └── config.toml
```

---

## ⚙️ Installation (Local Setup)

```bash
git clone https://github.com/seneeraj/AI-Cowork-Automated-Office
cd clarity-ai

pip install -r requirements.txt

streamlit run app.py
```

---

## 🔐 Environment Variables / Secrets

Create `.streamlit/secrets.toml` (for local) or add in Streamlit Cloud:

```toml
EMAIL="your_email@gmail.com"
PASSWORD="your_app_password"

TWILIO_SID="your_sid"
TWILIO_TOKEN="your_token"

OPENAI_API_KEY="your_openai_key"
```

---

## ☁️ Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to Streamlit Cloud
3. Select repository
4. Set `app.py` as entry point
5. Add secrets
6. Deploy 🚀

---

## ⚠️ Limitations

* SQLite resets on redeploy (Streamlit Cloud limitation)
* WhatsApp requires Twilio sandbox setup
* Email sending depends on SMTP limits

---

## 🚀 Future Enhancements

* 🔐 User authentication (multi-user SaaS)
* 📊 Advanced analytics dashboard
* 🤖 Auto-scheduled workflows
* 📅 Calendar integration
* 📈 Real-time business insights
* ☁️ Deployment on AWS / Docker

---

## 💼 Use Cases

* Small business automation
* Customer communication
* Internal operations management
* Marketing & outreach
* Data-driven decision making

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork the repo and submit a PR.

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Built with ❤️ to simplify business operations using AI.

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

---

