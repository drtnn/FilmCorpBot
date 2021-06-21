import asyncio
from bot import bot
import config
import download_video
import json
from logger import logging
from models import Movie, Video
import send_movie
import threading
import time
from upload_client import UploadClient


def get_queue():
    return json.loads(open(config.QUEUEFILE, 'r').read())


def set_queue(queue: list):
    with open(config.QUEUEFILE, 'w') as write_file:
        json.dump(queue, write_file)


def add_to_que(chat_id: int, movie_id: int, link: str, number=None, title=None):
    movie = Movie.select().where(Movie.movie_id == movie_id).first()
    if movie:
        queue = get_queue()
        if not number and movie.is_series:
            number = 0
            for movie_dict in queue:
                if movie_dict['movie_id'] == movie_id and movie_dict['number'] >= number:
                    number = movie_dict['number'] + 1
        number = (
            movie.to_videos()[-1].number + 1 if movie.to_videos() else 1) if movie.is_series and not number else number
        media = {'filename': f'{movie_id}-{number}.mp4', 'link': link, 'chat_id': chat_id, 'movie_id': movie_id,
                 'number': number,
                 'title': title}
        queue.append(media)
        logging.info(f'Adding video to queue: {json.dumps(queue)}')
        set_queue(queue)
        return media


async def client_sending_video(movie_dict: dict):
    loop = asyncio.new_event_loop()
    client = UploadClient(session_name='first', loop=loop)
    await client.start()
    file_id = await client.send_files(entity=config.BOTNAME, files=[config.DOWNLOADDIR + movie_dict['filename']],
                                      delete_on_success=True, print_file_id=True)
    await client.disconnect()
    return file_id


def upload_video(movie_dict: dict):
    try:
        download_video.download_video(movie_dict)
        file_id = asyncio.run(client_sending_video(movie_dict))
        video = Video.from_movie(movie_dict['movie_id'], file_id,
                                 movie_dict['number'] if movie_dict['number'] != 0 else None, movie_dict['title'])
        video.save()
        bot.send_message(movie_dict['chat_id'], f'Видео \'{movie_dict["filename"]}\' загружено!')
        send_movie.send_video(movie_dict['chat_id'], video.video_id)
    except Exception as e:
        bot.send_message(movie_dict['chat_id'], f'Ошибка при загрузке \'{movie_dict["filename"]}\'!\n\nException: {e}')


def infinite_download():
    while True:
        queue = get_queue()
        if queue:
            upload_video(queue[0])
            current_queue = get_queue()
            current_queue.pop(0)
            set_queue(current_queue)
        else:
            time.sleep(10)


infinite_loop = threading.Thread(name='infinite_loop', target=infinite_download)
