import uuid
import json
import os
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from psycopg2.pool import SimpleConnectionPool

# =========================================================
# CONFIG
# =========================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "Chatbot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "Postgres")
}

OLLAMA_API_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2:0.5b")

MAX_HISTORY = 20

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SessionAIChat")

# =========================================================
# APP
# =========================================================

app = FastAPI(title="SessionAIChat API")

# =========================================================
# DB CONNECTION POOL
# =========================================================

try:
    db_pool = SimpleConnectionPool(1, 10, **DB_CONFIG)
    logger.info("Database pool created")
except Exception as e:
    logger.error(f"DB Pool Error: {e}")
    raise

def get_db_conn():
    try:
        return db_pool.getconn()
    except Exception as e:
        logger.error(f"DB connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def release_db_conn(conn):
    db_pool.putconn(conn)

# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    user_id: int | None = None
    session_id: str | None = None
    message: str

# =========================================================
# UTIL
# =========================================================

def create_session_id():
    return str(uuid.uuid4())

# =========================================================
# DB OPERATIONS
# =========================================================

def create_conversation():
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        # Step 1: Create user
        cur.execute("INSERT INTO users DEFAULT VALUES RETURNING user_id")
        user_id = cur.fetchone()[0]

        # Step 2: Create session
        session_id = create_session_id()

        cur.execute(
            """
            INSERT INTO session_management (user_id, session_id, history)
            VALUES (%s, %s, %s)
            """,
            (user_id, session_id, '[]')
        )

        conn.commit()
        logger.info(f"New user {user_id}, session {session_id}")

        return user_id, session_id

    except Exception as e:
        conn.rollback()
        logger.error(f"Create conversation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

    finally:
        cur.close()
        release_db_conn(conn)


def create_new_session(user_id: int):
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        session_id = create_session_id()

        cur.execute(
            """
            INSERT INTO session_management (user_id, session_id, history)
            VALUES (%s, %s, %s)
            """,
            (user_id, session_id, '[]')
        )

        conn.commit()
        logger.info(f"New session {session_id} for user {user_id}")

        return session_id

    except Exception as e:
        conn.rollback()
        logger.error(f"Create session error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

    finally:
        cur.close()
        release_db_conn(conn)


def get_conversation(user_id, session_id):
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT history
            FROM session_management
            WHERE user_id = %s AND session_id = %s
            """,
            (user_id, session_id)
        )

        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Session not found")

        return row[0]

    finally:
        cur.close()
        release_db_conn(conn)


def update_conversation(user_id, session_id, history):
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE session_management
            SET history = %s
            WHERE user_id = %s AND session_id = %s
            """,
            (json.dumps(history), user_id, session_id)
        )

        conn.commit()

    except Exception as e:
        conn.rollback()
        logger.error(f"Update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update conversation")

    finally:
        cur.close()
        release_db_conn(conn)

# =========================================================
# HEALTH CHECK (GOOD PRACTICE)
# =========================================================

@app.get("/")
def health_check():
    return {"status": "SessionAIChat API is running 🚀"}

# =========================================================
# CHAT ENDPOINT
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    # -------- SESSION HANDLING --------

    if not request.user_id:
        if request.session_id:
            raise HTTPException(
                status_code=400,
                detail="Do not provide session_id for new user"
            )
        user_id, session_id = create_conversation()

    elif request.user_id and not request.session_id:
        user_id = request.user_id
        session_id = create_new_session(user_id)

    else:
        user_id = request.user_id
        session_id = request.session_id
        history = get_conversation(user_id, session_id)

    # -------- HISTORY --------

    history = history if 'history' in locals() else []

    history.append({
        "role": "user",
        "content": request.message
    })

    history = history[-MAX_HISTORY:]

    # -------- MODEL CALL --------

    payload = {
        "model": OLLAMA_MODEL,
        "messages": history,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        assistant_reply = data.get("message", {}).get("content", "")

    except Exception as e:
        logger.error(f"Model API error: {e}")
        raise HTTPException(status_code=500, detail="Model API failed")

    # -------- SAVE RESPONSE --------

    history.append({
        "role": "assistant",
        "content": assistant_reply
    })

    update_conversation(user_id, session_id, history)

    return {
        "user_id": user_id,
        "session_id": session_id,
        "response": assistant_reply
    }

# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)