from bot import bot
import config
from logger import logging
from models import User, Video, Movie
import register_next_step
import search_movie
import send_movie
from telebot import types


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Привет! Пришли название фильма/сериала!')
    try:
        User.change_or_create(user_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name).save()
    except:
        bot.send_message(config.ADMIN[0], f'user_id={message.from_user.id}, username={message.from_user.username}, first_name={message.from_user.first_name}')


@bot.message_handler(commands=['add_movie'])
def add_movie_command(message):
    if message.chat.id in config.ADMIN:
        bot.send_message(message.chat.id, 'Пришли мне ссылку на кинопоиск')
        bot.register_next_step_handler_by_chat_id(message.chat.id, register_next_step.register_movie)


@bot.message_handler(commands=['last_series'])
def last_series_command(message):
    if message.chat.id in config.ADMIN:
        movies = Movie.select().where(Movie.is_series == True).order_by(-Movie.movie_id).limit(15)
        keyboard = types.InlineKeyboardMarkup()
        for movie in movies:
            keyboard.add(types.InlineKeyboardButton(text=movie.to_key(), callback_data=f'{movie.movie_id}_addvideo'))
        bot.send_message(message.chat.id, 'Выбери сериал для добавления новой серии', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def text_message(message):
    search_movie.search_movie(message.chat.id, message.text)


@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    logging.info(f'{c.from_user.id} {c.from_user.username}: {c.data}')
    if c.data == 'delete_message':
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    elif c.data.endswith('_getvideo'):
        send_movie.send_video(chat_id=c.message.chat.id, video_id=int(c.data[:-9]), message_id=c.message.message_id)
    elif c.data.endswith('_getmovie'):
        send_movie.send_movie(chat_id=c.message.chat.id, movie_id=int(c.data[:-9]), message_id=c.message.message_id)
    elif c.from_user.id in config.ADMIN:
        if c.data.endswith('_addvideo'):
            bot.send_message(c.message.chat.id, 'Пришли мне видео или ссылку на скачивание')
            bot.register_next_step_handler_by_chat_id(c.message.chat.id, register_next_step.register_video, int(c.data[:-9]))
        elif c.data.endswith('_videonumber'):
            old_message = bot.send_message(c.message.chat.id, 'Пришли номер серии')
            bot.register_next_step_handler_by_chat_id(chat_id=c.message.chat.id,
                                                      callback=register_next_step.register_video_info,
                                                      video_id=int(c.data[:-12]), type='number',
                                                      old_message_id=old_message.message_id,
                                                      tapped_message_id=c.message.message_id)
        elif c.data.endswith('_videotitle'):
            old_message = bot.send_message(c.message.chat.id, 'Пришли название серии')
            bot.register_next_step_handler_by_chat_id(chat_id=c.message.chat.id,
                                                      callback=register_next_step.register_video_info,
                                                      video_id=int(c.data[:-11]), type='title',
                                                      old_message_id=old_message.message_id,
                                                      tapped_message_id=c.message.message_id)
        elif c.data.endswith('_tryvideodelete'):
            register_next_step.register_are_you_sure(chat_id=c.message.chat.id, type='videodelete', video_id=c.data[:-15])
        elif c.data.endswith('_videodelete'):
            try:
                bot.delete_message(c.message.chat.id, c.message.message_id)
            except:
                pass
            Video.delete_by_video_id(video_id=int(c.data[:-12]))
        elif c.data.endswith('_movieseason'):
            old_message = bot.send_message(c.message.chat.id, 'Пришли номер сезона')
            bot.register_next_step_handler_by_chat_id(chat_id=c.message.chat.id,
                                                      callback=register_next_step.register_movie_info,
                                                      movie_id=int(c.data[:-12]), type='season',
                                                      old_message_id=old_message.message_id,
                                                      tapped_message_id=c.message.message_id)