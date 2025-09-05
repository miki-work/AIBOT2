import os#
import requests #для отправки HTTP-запросов к OllamaAPI(чтобы спросить у ИИ)
from PIL import Image#для обработки изображений
import tempfile#для создания временных файлов при обработке фото

#Основные классы из библиотеки python-telegram-bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import logging#для логов
import sqlite3#для работы с БД
from datetime import datetime#для сохранения времени сообщения
from dotenv import load_dotenv#для загрузки токена из /env

load_dotenv()#этим мы загружаем уже токен

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

#создаем таблицу автоматически
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


#сохраняем сообщение
def save_message(user_id: int, username: str, msg_type: str, user_input: str, ai_response: str):
    """Сохраняет сообщение и ответ ИИ в базу"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (user_id, username, message_type, user_input, ai_response, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, msg_type, user_input, ai_response, datetime.now().isoformat())
        )
    logger.info(f"Сообщение от {username} сохранено в БД.")

#отклик на команду start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие"""
    await update.message.reply_text("Привет! Отправь текст или фото — я отвечу. История сохраняется!")
    logger.info(f"Пользователь {update.effective_user.username} запустил бота.")

#обробатывает текстовый запрос
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_text = update.message.text
    logger.info(f"Получен текст от {user.username}: {user_text}")

    try:
        #отправляет запрос к Ollama
        response = requests.post(
            OLLAMA_API,
            json={
                "model": MODEL,
                "prompt": user_text,
                "stream": False
            }
        )
        response.raise_for_status()
        ai_answer = response.json()["response"]
    except Exception as e:
        ai_answer = f"Ошибка ИИ: {e}"
        logger.error(f"Ошибка при генерации текста: {e}")

    #отправляет ответ
    await update.message.reply_text(ai_answer)

# Сохраняем в БД
    save_message(
        user_id=user.id,
        username=user.username,
        msg_type="text",
        user_input=user_text,
        ai_response=ai_answer
    )

#обробатывает фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.effective_user
    
    #получаю файл фото
    photo_file = await update.message.photo[-1].get_file()
    
    #создаёт временный файл, чтобы сохранить фото
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        await photo_file.download_to_drive(tmp_file.name)
        image_path = tmp_file.name

    try:
        image = Image.open(image_path)
        logger.info(f"Фото загружено: {image_path}")
        #готовит промпт
        prompt = "Опиши, что изображено на фото, детально."
        with open(image_path, "rb") as img_file:
            import base64
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

        #отправляет запрос к Ollama с фото
        response = requests.post(
            OLLAMA_API,
            json={
                "model": MODEL,
                "prompt": prompt,
                "images": [encoded_image],
                "stream": False
            }
        )

        response.raise_for_status()
        ai_answer = response.json()["response"]
    except Exception as e:
        ai_answer = f"Ошибка при анализе фото: {e}"
        logger.error(f"Ошибка при обработке фото: {e}")
    finally:
        #удаляю временный файл чтобы не засорять диск
        os.unlink(image_path)

    #отправляет ответ
    await update.message.reply_text(ai_answer)

    # Сохраняем в БД
    save_message(
        user_id=user.id,
        username=user.username,
        msg_type="photo",
        user_input="Пользователь отправил фото",
        ai_response=ai_answer
    )


#запуск бота
def main():
   
    init_db()  # Инициализация БД при старте

    #создаю приложение апп с токеном
    app = Application.builder().token(TOKEN).build()

    #добавляю обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    #получение обновлений от Telegram
    logger.info("Бот запущен. Ожидание сообщений...")
    app.run_polling()

#если файл запускается напрямую, запускаем main()
if __name__ == "__main__":
    main()
