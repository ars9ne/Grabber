import re
import os
import logging
import subprocess
import time
import sys
import pytube
import telegram
import languages
from pytube import YouTube
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

script_directory = os.path.dirname(os.path.abspath(__file__))
token = str(sys.argv[1])  # token

lang_manager = languages.LanguageManager()
lang_manager.set_language('russian')
mtext = lang_manager.get_text  # message text

# Включение логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда пользователь вводит команду /start."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Вы можете загрузить любое видео с YouTube или Twitter. Просто отправьте ссылку на него:",
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
        await update.message.reply_text(mtext("mp3selected"))
    elif command == "/mp4":
        context.user_data["format"] = "mp4"
        await update.message.reply_text(mtext("mp4selected"))
    elif command == "/language":
        context.user_data["languages"] = "english"
        await update.message.reply_text("Select preferable language: /russian , /english")
    elif command == "/english":
        context.user_data["languages"] = "english"
        lang_manager.set_language("english")
        await update.message.reply_text(lang_manager.get_text('languageselected'))
    elif command == "/russian":
        context.user_data["languages"] = "russian"
        lang_manager.set_language("russian")
        await update.message.reply_text(lang_manager.get_text('languageselected'))
    else:
        pass

    # Отправить сообщение с выбранным форматом
    format = context.user_data.get("format", "mp4")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда пользователь вводит команду /help."""
    await update.message.reply_text(mtext("start"))


async def send_format_choice(update: Update) -> None:
    keyboard = [
        [
            InlineKeyboardButton("MP4 (Видео)", callback_data="mp4"),
            InlineKeyboardButton("MP3 (Аудио)", callback_data="mp3"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(mtext("choose_format"), reply_markup=reply_markup)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Функция эхо, не используется."""
    await update.message.reply_text("OK")


async def is_link(text: str) -> bool:
    """Проверяет, является ли сообщение ссылкой."""
    if "youtube.com/watch" in text or "youtu.be/" in text or "youtube.com/shorts" in text or "twitter.com" in text or "x.com" in text:
        return True
    else:
        return False


def sanitize_filename(filename: str) -> str:
    """Заменяет ненужные символы на _"""
    return re.sub(r"[^\w\-_ ]", "_", filename.replace(" ", "_"))


async def log_message(chat_id: int, username: str, text: str) -> None:
    """Логирует сообщения от пользователей."""
    with open("messages_log.txt", "a", encoding="utf-8") as log_file:
        # log_file.write(f"ChatID: {chat_id} Username: {username} Message: {text}\n") по желанию)
        pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает сообщения."""
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    text = update.message.text

    # Логирование сообщения в текстовый файл
    await log_message(chat_id, username, text)

    if await is_link(text):
        logger.info("Получена ссылка!")
        if "youtube.com/watch" in text or "youtu.be/" in text or "youtube.com/shorts" in text:
            # Запуск download_script.py с аргументами в виде ссылки и формата
            desired_format = context.user_data.get("format", "mp3")
            yt = YouTube(text)
            if yt.streams.get_by_itag(18).filesize < 49999550:
                result = subprocess.run(["python", "download_script.py", text, desired_format], capture_output=True,
                                        text=True, encoding="utf-8")
                if result.returncode == 0:
                    await update.message.reply_text(mtext("sendfilenoti"))
                    print("файл ок")
                    # Получение тайтла видео

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
                await update.message.reply_text(mtext("file_too_large"))


        elif "twitter.com" in text or "x.com" in text:
            text = text.replace("twitter.com", "fxtwitter.com")
            # Запуск download_script.py с аргументами в виде ссылки и формата
            desired_format = context.user_data.get("format", "mp3")
            if str(desired_format) == "mp4":
                text = text + ".mp4"

                result = subprocess.run(["python", "download_script.py", text, desired_format], capture_output=True,
                                        text=True, encoding="utf-8")
                if result.returncode == 0:
                    await update.message.reply_text(mtext("sendfilenoti"))

                    # Получение тайтла видео

                    video_title = "video_name"

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
            elif str(desired_format) == "mp3":
                await update.message.reply_text(mtext("not_available"))
        else:
            await update.message.reply_text(mtext("link_processing_error"))
    else:
        await update.message.reply_text(mtext("not_a_link"))


def main() -> None:
    """Запускает бота."""
    # Создание приложения и передача ему токена бота.
    application = Application.builder().token(token).write_timeout(200).read_timeout(200).connect_timeout(200).build()

    # Обработка команд
    application.add_handler(CommandHandler(["mp3", "mp4", "language", "english", "russian"], handle_command))

    # Обработка всех текстовых сообщений, не являющихся командами
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
