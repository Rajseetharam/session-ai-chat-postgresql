# 🚀 SessionAIChat – FastAPI Chatbot Backend with PostgreSQL

A **production-ready AI chatbot backend** built using **FastAPI** and **PostgreSQL**, supporting **session-based conversation management** and persistent chat history.

---

## 📌 Overview

SessionAIChat is a scalable backend system designed to handle conversational AI workflows. It enables users to maintain multiple chat sessions with stored history using PostgreSQL.

---

## ⚙️ Tech Stack

* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL
* **ORM/Driver:** psycopg2 / psycopg
* **API Testing:** Swagger UI (built-in)
* **AI Model:** Ollama (local LLM)

---

## ✨ Features

- ✅ Multi-user support  
- ✅ Multi-session management per user  
- ✅ Session-based chat system  
- ✅ Persistent conversation history (JSONB)  
- ✅ PostgreSQL optimized schema  
- ✅ RESTful API design  
- ✅ Scalable architecture  
- ✅ Connection pooling for performance  
- ✅ Error handling and logging  

---

## 📂 Project Structure

```
SessionAIChat/
│
├── app.py               # Main FastAPI application
├── schema.sql           # Database schema (DDL)
├── requirements.txt     # Dependencies
├── .gitignore
└── README.md
```

---

## 🗄️ Database Design

### Tables:

1. **users**

   * Stores user records

2. **session_management**

   * Stores session_id and chat history
   * Uses JSONB for flexible storage

---

## 🚀 Getting Started

### 1️⃣ Clone Repository

```
git clone https://github.com/Rajseetharam/session-ai-chat-postgresql.git
cd session-ai-chat-postgresql
```

---

### 2️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Setup Database

Create database:

```
CREATE DATABASE Chatbot;
```

Run schema:

```
psql -U postgres -d Chatbot -f schema.sql
```

---

### 5️⃣ Run Application

```
uvicorn app:app --reload --port 8080
```

---

## 📡 API Endpoints

### 🔹 POST `/chat`

Send message to chatbot

#### Request:

```
{
  "user_id": null,
  "session_id": null,
  "message": "Hello"
}
```

#### Response:

```
{
  "user_id": 1,
  "session_id": "uuid",
  "response": "Hello! How can I help you?"
}
```

---

## 📘 API Documentation

Once running, open:

👉 http://127.0.0.1:8080/docs

---

## 🧠 How It Works

* New users → new user + session created
* Existing users → new session or reuse session
* Messages stored in PostgreSQL JSONB
* Last 20 messages used as context

