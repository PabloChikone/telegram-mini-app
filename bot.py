import telebot
from telebot.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8049653255:AAG6_l6QYxGjleAYuqwAQHUwQO-nqJaUx6Y"
# Твоя ссылка на GitHub Pages (обязательно с https и слэшем в конце)
WEB_APP_URL = "https://pablochikone.github.io/telegram-mini-app/"
# -----------------

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем клавиатуру с кнопкой Web App
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    # Кнопка, которая открывает мини-апп
    btn = KeyboardButton(text="🚀 Запустить приложение", web_app=WebAppInfo(url=WEB_APP_URL))
    markup.add(btn)

    bot.send_message(
        message.chat.id,
        f"Привет! Я твой тестовый бот.\nНажми кнопку ниже, чтобы открыть мини-приложение:\n\n🌐 Ссылка: {WEB_APP_URL}",
        reply_markup=markup
    )


print(f"Бот запущен... Открывает URL: {WEB_APP_URL}")
bot.infinity_polling()