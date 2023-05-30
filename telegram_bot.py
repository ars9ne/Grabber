import re
import os
import logging
import subprocess
import time
import sys
import pytube
from pytube import YouTube
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
script_directory = os.path.dirname(os.path.abspath(__file__))
token = str(sys.argv[1]) #получаем token телеграмм бота в виде аргумента при запуске скрипта

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
    await send_format_choice(update)

async def handle_format_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()

    # Сохраните выбранный формат в пользовательских данных
    context.user_data["format"] = query.data
    await query.edit_message_text(text=f"Выбранный формат: {query.data}. Теперь отправьте ссылку на видео.")


async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команды."""
    command = update.message.text.lower()
    if command == "/mp3":
        context.user_data["format"] = "mp3"
        await update.message.reply_text("Выбран формат mp3. Отправьте ссылку на видео для загрузки.")
    elif command == "/mp4":
        context.user_data["format"] = "mp4"
        await update.message.reply_text("Выбран формат mp4. Отправьте ссылку на видео для загрузки.")
    else:
        await update.message.reply_text("Неверная команда. Используйте /mp3 или /mp4 для выбора формата загрузки.")

    # Отправить сообщение с выбранным форматом
    format = context.user_data.get("format", "mp4")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда пользователь вводит команду /help."""
    await update.message.reply_text("Вы можете загрузить любое видео с YouTube или TikTok! Просто скинь ссылку на видео")

async def send_format_choice(update: Update) -> None:
    keyboard = [
        [
            InlineKeyboardButton("MP4 (Видео)", callback_data="mp4"),
            InlineKeyboardButton("MP3 (Аудио)", callback_data="mp3"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите формат для загрузки видео:", reply_markup=reply_markup)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Функция эхо, не используется."""
    await update.message.reply_text("OK")

async def is_link(text: str) -> bool:
    """Проверяет, является ли сообщение ссылкой."""
    if "www.youtube.com/watch" in text or "youtu.be/" in text:
        return True
    else:
        return False

def sanitize_filename(filename: str) -> str:
    """Заменяет ненужные символы на _"""
    return re.sub(r"[^\w\-_ ]", "_", filename.replace(" ", "_"))


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

        # Запуск download_script.py с аргументами в виде ссылки и формата
        desired_format = context.user_data.get("format", "mp3")
        result = subprocess.run(["python", "download_script.py", text, desired_format], capture_output=True, text=True, encoding="utf-8")
        if result.returncode == 0:
            await update.message.reply_text("Файл загружен. Отправляю вам его...")

            # Получение тайтла видео
            yt = YouTube(text)
            video_title = sanitize_filename(yt.title)

            # Поиск пути файла на основе полученных форматов
            if desired_format == "mp3":
                file_name = video_title + ".mp3"
            else:
                file_name = video_title + ".mp4"

            file_path = os.path.join(script_directory, file_name)

            # Отправка видео пользователю
            with open(file_path, "rb") as f:
                await context.bot.send_document(chat_id=chat_id, document=f)

            # удаление загруженного файла
            os.remove(file_path)
        else:
            await update.message.reply_text("Ошибка при обработке ссылки. Попробуйте еще раз.")
    else:
        await update.message.reply_text("Это не ссылка. Пожалуйста, отправьте мне ссылку на видео YouTube или TikTok.")


def main() -> None:
    """Запускает бота."""
    # Создание приложения и передача ему токена бота.
    application = Application.builder().token(token).build()

    # Обработка команд
    application.add_handler(CommandHandler(["mp3", "mp4"], handle_command))

    # Обработка всех текстовых сообщений, не являющихся командами
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()