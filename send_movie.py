import config
from bot import bot
from models import Movie, Video
from telebot import types


def send_movie(chat_id: int, movie_id: int, message_id=None):
    movie = Movie.select().where(Movie.movie_id == movie_id)
    keyboard = types.InlineKeyboardMarkup()
    if movie:
        movie = movie.first()
        videos = movie.to_videos()
        if not movie.is_series and videos:
            keyboard.add(types.InlineKeyboardButton(text='📼 Фильм' + (f': {movie.title}' if movie.title else ''),
                                                    callback_data=f'{videos[0].video_id}_getvideo'))
        elif videos:
            for video in videos.order_by(Video.number):
                keyboard.add(
                    types.InlineKeyboardButton(
                        text=f'📼 {video.number} серия{f": {video.title}" if video.title else ""}',
                        callback_data=f'{video.video_id}_getvideo'))
        if chat_id in config.ADMIN:
            keyboard.add(
                types.InlineKeyboardButton(
                    text='📼 Добавить серию' if movie.is_series else '📼 Добавить фильм',
                    callback_data=f'{movie.movie_id}_addvideo'))
            if movie.is_series:
                keyboard.add(
                    types.InlineKeyboardButton(
                        text='📼 Изменить номер сезона',
                        callback_data=f'{movie.movie_id}_movieseason'))
    else:
        return bot.send_message(chat_id=chat_id,
                                text="Фильм/сериал не найден!",
                                parse_mode='html')
    keyboard.add(types.InlineKeyboardButton(text='🎥 Ссылка на Кинопоиск', url=movie.kinopoisk))
    try:
        bot.edit_message_media(chat_id=chat_id,
                               message_id=message_id,
                               media=types.InputMediaPhoto(movie.cover))
        return bot.edit_message_caption(chat_id=chat_id, caption=movie.to_message(), message_id=message_id,
                                        parse_mode='html',
                                        reply_markup=keyboard)
    except:
        return bot.send_photo(chat_id=chat_id,
                              photo=movie.cover,
                              caption=movie.to_message(),
                              parse_mode='html',
                              reply_markup=keyboard)


def send_video(chat_id: int, video_id: int, message_id=None):
    video = Video.select().where(Video.video_id == video_id).first()
    keyboard = types.InlineKeyboardMarkup()
    if video:
        previous_series = Video.select().where(
            (Video.movie == video.movie) & (
                    Video.number < video.number)).order_by(-Video.number).first() if video.number else None
        next_series = Video.select().where(
            (Video.movie == video.movie) & (
                    Video.number > video.number)).order_by(Video.number).first() if video.number else None
        if previous_series and next_series and video.movie.is_series:
            keyboard.row(types.InlineKeyboardButton(f'📼 {previous_series.number} серия',
                                                    callback_data=f'{previous_series.video_id}_getvideo'),
                         types.InlineKeyboardButton(f'📼 {next_series.number} серия',
                                                    callback_data=f'{next_series.video_id}_getvideo'))
        elif previous_series and video.movie.is_series:
            keyboard.add(types.InlineKeyboardButton(f'📼 {previous_series.number} серия',
                                                    callback_data=f'{previous_series.video_id}_getvideo'))
        elif next_series and video.movie.is_series:
            keyboard.add(types.InlineKeyboardButton(f'📼 {next_series.number} серия',
                                                    callback_data=f'{next_series.video_id}_getvideo'))
        if chat_id in config.ADMIN:
            if video.movie.is_series:
                keyboard.add(types.InlineKeyboardButton(text='Изменить номер серии',
                                                        callback_data=f'{video.video_id}_videonumber'))
            keyboard.add(
                types.InlineKeyboardButton(text='Изменить название', callback_data=f'{video.video_id}_videotitle'))
            keyboard.add(
                types.InlineKeyboardButton(text='⚠ Удалить видео️', callback_data=f'{video.video_id}_tryvideodelete'))
        keyboard.add(types.InlineKeyboardButton('🎞 К сериалу' if video.movie.is_series else '🎞 К фильму',
                                                callback_data=f'{video.movie.movie_id}_getmovie'))
        try:
            bot.edit_message_media(chat_id=chat_id, media=types.InputMediaVideo(video.file_id), message_id=message_id)
            return bot.edit_message_caption(chat_id=chat_id, caption=video.to_message(), message_id=message_id,
                                            parse_mode='html', reply_markup=keyboard)
        except:
            return bot.send_video(chat_id, video.file_id, caption=video.to_message(), parse_mode='html',
                                  reply_markup=keyboard)
    else:
        bot.send_message(chat_id=chat_id,
                         text="Видео не найдено!",
                         parse_mode='html')
