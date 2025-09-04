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
