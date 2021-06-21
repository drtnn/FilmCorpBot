from bot import bot
import config
import send_movie
from models import Movie, Video
from telebot import types
import upload_video


def register_video_info(message, video_id: int, type: str, old_message_id: int, tapped_message_id: int):
    if message.text == '/cancel':
        return
    video = Video.select().where(Video.video_id == video_id).first()
    if video and type == 'number':
        video.number = int(message.text)
        video.save()
    elif video and type == 'title':
        video.title = message.text
        video.save()
    else:
        return
    try:
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, old_message_id)
    except:
        pass
    send_movie.send_video(message.chat.id, video.video_id, tapped_message_id)


def register_video(message, movie_id: int, number=None, title=None):
    if message.text == '/cancel':
        return
    movie = Movie.select().where(Movie.movie_id == movie_id).first()
    if message.video:
        if movie and message.video:
            video = Video.from_movie(movie_id, message.video.file_id, number, title)
            video.save()
            send_movie.send_video(message.chat.id, video.video_id)
            return video
        elif movie:
            bot.send_message(message.chat.id, 'Пришли мне видео')
            bot.register_next_step_handler_by_chat_id(message.chat.id, register_video, movie_id)
        else:
            bot.send_message(chat_id=message.chat.id, text='Фильм/сериал не найден!')
    else:
        upload_video.add_to_que(chat_id=message.chat.id, movie_id=movie_id, link=message.text)


def register_are_you_sure(chat_id: int, type: str, video_id=None):
    keyboard = types.InlineKeyboardMarkup()
    if type == 'videodelete':
        keyboard.row(types.InlineKeyboardButton(text='Да!', callback_data=f'{video_id}_videodelete'), types.InlineKeyboardButton(text='Нет!', callback_data=f'delete_message'))
        return bot.send_message(chat_id, 'Ты уверен, что хочешь удалить данное видео?', reply_markup=keyboard)


def register_movie_info(message, movie_id: int, type: str, old_message_id: int, tapped_message_id: int):
    if message.text == '/cancel':
        return
    movie = Movie.select().where(Movie.movie_id == movie_id).first()
    if movie and type == 'season':
        movie.season = int(message.text)
        movie.save()
    else:
        return
    try:
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, old_message_id)
    except:
        pass
    send_movie.send_movie(message.chat.id, movie.movie_id, tapped_message_id)


def register_movie(message):
    if message.text == '/cancel':
        return
    try:
        movie = Movie.from_kinopoisk(message.text)
        movie.save()
        send_movie.send_movie(message.chat.id, movie.movie_id)
    except:
        bot.send_message(message.chat.id, 'Неверная ссылка. Пришли мне новую ссылку на кинопоиск')
        bot.register_next_step_handler_by_chat_id(message.chat.id, register_movie)
