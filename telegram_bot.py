import re
import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Включение логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда пользователь вводит команду /start."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Вы можете загрузить любое видео с YouTube или TikTok. Просто отправьте ссылку на него:",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда пользователь вводит команду /help."""
    await update.message.reply_text("Вы можете загрузить любое видео с YouTube или TikTok! Просто скинь ссылку на видео")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Функция эхо, не используется."""
    await update.message.reply_text("OK")

async def is_link(text: str) -> bool:
    """Проверяет, является ли сообщение ссылкой."""
    if "www.youtube.com/watch" in text or "youtu.be/" in text:
        return True
    else:
        return False

async def log_message(chat_id: int, username: str, text: str) -> None:
    """Логирует сообщения от пользователей."""
    with open("messages_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"ChatID: {chat_id} Username: {username} Message: {text}\n")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает сообщения."""
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    text = update.message.text

    # Логирование сообщения в текстовый файл
    await log_message(chat_id, username, text)

    if await is_link(text):
        logger.info("Получена ссылка!")
        await update.message.reply_text("OK")
    else:
        await update.message.reply_text("Это не ссылка. Пожалуйста, отправьте мне ссылку на видео YouTube или TikTok.")

def main() -> None:
    """Запускает   бота."""
    # Создание приложения и передача ему токена бота.
    application = Application.builder().token("082210671:AAEy0qYiVCkXzdiTNDNaLjvUFPgi2W6i-4U").build()

    # Обработка различных команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Обработка всех текстовых сообщений, не являющихся командами
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
