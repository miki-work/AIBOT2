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
