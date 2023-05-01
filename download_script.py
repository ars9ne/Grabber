import os
import subprocess
from pytube import YouTube
import time

time1 = time.time()

link = "https://www.youtube.com/watch?v=MKihQV18qA4"  # Ссылка на видео
orr = 'mp3' # mp3 или mp4

yt = YouTube(link)  # Cоздадим объект класса YouTube, и в качестве значения передадим введённую пользователем ссылку

if orr == 'mp4': # если запросили видео
    ys = yt.streams.get_highest_resolution() # Получим максимально возможное разрешение видео

    ys.download('C:/Users/bkree/Desktop') # Загружаем
    print("Загрузка завершена!")
    print("--- %s seconds ---" % (time.time() - time1)) # Время загрузки
# если запросили аудио
else:
    # извлекаем только аудио
    video = yt.streams.filter(only_audio=True).first()

    # проверяем пункт назначения для сохранения файла
    destination = 'C:/Users/bkree/Desktop' or '.'

    # загружаем файл
    out_file = video.download(output_path=destination)

    # сохраняем файл
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)

    # результат
    print(yt.title + " has been successfully downloaded.")