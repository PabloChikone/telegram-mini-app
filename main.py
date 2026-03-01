import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import telebot
from telebot.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import psycopg2
import pandas as pd
from datetime import date

# Загрузка переменных из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = "https://pablochikone.github.io/telegram-mini-app/"  # Ссылка на фронтенд

# Настройки БД
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# --- ЧАСТЬ 1: API СЕРВЕР (Для данных) ---
app = FastAPI()

# Разрешаем CORS, чтобы GitHub Pages мог стучаться к нам
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретный домен github.io
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_data_from_db():
    """Получает данные из PostgreSQL и возвращает список словарей"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = """
            SELECT date, successful_tmk_count, last_modified_time 
            FROM zpv_max 
            ORDER BY date ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()

        # Преобразуем даты в строки для JSON
        df['date'] = df['date'].astype(str)
        df['last_modified_time'] = df['last_modified_time'].astype(str)

        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return []


@app.get("/api/data")
def read_data():
    data = get_data_from_db()
    return {"status": "ok", "data": data}


# --- ЧАСТЬ 2: TELEGRAM БОТ ---
bot = telebot.TeleBot(BOT_TOKEN, use_class_middlewares=True)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = KeyboardButton(text="📊 Открыть Дашборд", web_app=WebAppInfo(url=WEB_APP_URL))
    markup.add(btn)
    bot.send_message(message.chat.id, "Жми кнопку, чтобы увидеть статистику из БД!", reply_markup=markup)


# --- ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке, чтобы не блокировать API
    import threading

    thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    thread.start()

    print("Бот запущен. API сервер стартует...")
    # Запускаем API сервер на порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)