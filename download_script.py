import os
import subprocess
from pytube import YouTube
import time
import sys
import uuid
import re
script_directory = os.path.dirname(os.path.abspath(__file__))
#пункт назначения для сохранения файла
destination = script_directory

time1 = time.time()

link = str(sys.argv[1])  # Ссылка на видео
orr = str(sys.argv[2])  # mp3 или mp4
yt = YouTube(link)  # Cоздадим объект класса YouTube, и в качестве значения передадим введённую пользователем ссылку

def sanitize_filename(filename: str) -> str:
    """Заменяет ненужные символы на _"""
    return re.sub(r"[^\w\-_ ]", "_", filename.replace(" ", "_"))

if orr == 'mp4':  # если запросили видео
    ys = yt.streams.get_highest_resolution()  # Получим максимально возможное разрешение видео

    # Загружаем, используя очищенное название файла с расширением .mp4
    sanitized_title = sanitize_filename(yt.title)
    ys.download(destination, filename=f"{sanitized_title}.mp4")

    print("Загрузка завершена!")
    print("--- %s seconds ---" % (time.time() - time1))  # Время загрузки

# если запросили аудио
else:
    # извлекаем только аудио
    video = yt.streams.filter(only_audio=True).first()

    # загружаем файл
    out_file = video.download(output_path=destination, filename=sanitize_filename(yt.title))

    # сохраняем файл
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)

    # результат
    print(yt.title + " has been successfully downloaded.")