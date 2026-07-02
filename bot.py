import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_URL = os.getenv('APP_URL')
ALLOWED_USERS_STR = os.getenv('ALLOWED_USERS')

# Преобразуем строку из .env обратно в словарь
try:
    ALLOWED_USERS = json.loads(ALLOWED_USERS_STR)
except json.JSONDecodeError:
    print("Ошибка: Неверный формат ALLOWED_USERS в .env. Используйте валидный JSON.")
    ALLOWED_USERS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start. Проверяет пользователя и отправляет кнопку."""
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name

    # Проверяем, есть ли пользователь в списке разрешенных
    if user_id in ALLOWED_USERS:
        # Получаем имя из списка или используем имя из Telegram
        display_name = ALLOWED_USERS[user_id] if ALLOWED_USERS[user_id] else user_name
        message = (
            f"Привет, {display_name}! 👋\n"
            "Добро пожаловать в наше мини-приложение."
        )
        
        # Создаем кнопку для открытия мини-приложения
        keyboard = [[InlineKeyboardButton("Открыть мини-приложение", web_app={"url": APP_URL})]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, reply_markup=reply_markup)
    else:
        # Если пользователь не в списке
        await update.message.reply_text(
            "Извините, у вас нет доступа к этому боту и его приложению. 🚫"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик любых других сообщений."""
    user_id = str(update.effective_user.id)
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Доступ запрещен.")
        return
    
    # Если пользователь разрешен, можно обработать его сообщение
    # Например, отправить то же самое меню
    await start(update, context)

def main() -> None:
    """Запуск бота."""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота (для продакшена используйте webhook, но для теста подойдет polling)
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
