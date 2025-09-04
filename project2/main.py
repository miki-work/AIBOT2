import os
import requests
from PIL import Image
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#токен из .env
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден! Убедись, что файл .env существует и содержит TOKEN.")

# Ollama API
OLLAMA_API = "http://host.docker.internal:11434/api/generate"
MODEL = "llava"

# Путь к базе данны
DB_PATH = "bot_data.db"

def init_db():
    """Создаёт таблицу для истории диалогов"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message_type TEXT,  -- 'text' или 'photo'
                user_input TEXT,
                ai_response TEXT,
                timestamp TEXT
            )
        """)
    logger.info("База данных инициализирована.")

def save_message(user_id: int, username: str, msg_type: str, user_input: str, ai_response: str):
    """Сохраняет сообщение и ответ ИИ в базу"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (user_id, username, message_type, user_input, ai_response, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, msg_type, user_input, ai_response, datetime.now().isoformat())
        )
    logger.info(f"Сообщение от {username} сохранено в БД.")
