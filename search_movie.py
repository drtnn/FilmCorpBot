from bot import bot
from models import Movie
from peewee import fn
from telebot import types


def search_movie(chat_id: int, text: str):
    movies = Movie.select().where(fn.lower(Movie.title).contains(text.lower())).order_by(Movie.title, Movie.season).limit(10)
    keyboard = types.InlineKeyboardMarkup()
    for movie in movies:
        keyboard.add(types.InlineKeyboardButton(text=movie.to_key(), callback_data=f'{movie.movie_id}_getmovie'))
    if movies:
        bot.send_message(chat_id, f'Поиск по запросу: <i>{text}</i>', reply_markup=keyboard, parse_mode='html')
    else:
        bot.send_message(chat_id, 'Для просмотра ничего не найдено')
