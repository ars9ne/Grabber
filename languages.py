class RussianLang:
    sendfilenoti = "Файл загружен. Отправляю вам его..."
    mp3selected = "Выбран формат mp3. Отправьте ссылку на видео для загрузки."
    mp4selected = "Выбран формат mp4. Отправьте ссылку на видео для загрузки."
    start = "Вы можете загрузить любое видео с YouTube или Twitter. Просто отправьте ссылку на него:"
    invalid_command = "Неверная команда. Используйте /mp3 или /mp4 для выбора формата загрузки."
    help = "Вы можете загрузить любое видео с YouTube или Twitter! Просто отправьте ссылку на видео."
    choose_format = "Выберите формат для загрузки видео:"
    file_too_large = "Телеграм бот не может отправлять файл весом больше 50МБ"
    not_available = "Загрузка файлов в формате mp3 из твиттера не доступна"
    link_processing_error = "Ошибка при обработке ссылки. Попробуйте еще раз."
    not_a_link = "Это не ссылка. Пожалуйста, отправьте мне ссылку на видео YouTube или Twitter."
    languageselected = "Язык выбран"


class EnglishLang:
    sendfilenoti = "File uploaded. Sending it to you..."
    mp3selected = "mp3 format selected. Please send video link to download."
    mp4selected = "mp4 format selected. Send video link to download."
    start = "You can download any video from YouTube or Twitter. Just send a link to it:"
    invalid_command = "Invalid command. Use /mp3 or /mp4 to select download format."
    help = "You can download any video from YouTube or Twitter! Just send the video link."
    choose_format = "Choose a video upload format:"
    file_too_large = "Telegram bot cannot send files larger than 50MB"
    not_available = "Twitter mp3 download not available"
    link_processing_error = "An error occurred while processing the link. Please try again."
    not_a_link = "This is not a link. Please send me a link to a YouTube or Twitter video."
    languageselected = "Language selected"


class LanguageManager:
    def __init__(self, lang='english'):
        self.lang = lang.lower()

    def set_language(self, lang):
        self.lang = lang.lower()

    def get_language(self):
        return self.lang

    def get_text(self, key):
        lang_class = EnglishLang if self.lang == 'english' else RussianLang
        return getattr(lang_class, key, f"Translation for '{key}' not found in the current language.")
