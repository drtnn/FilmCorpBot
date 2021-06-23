from config import DATABASE_URL
import peewee
import requests
from bs4 import BeautifulSoup as BS

DB = peewee.PostgresqlDatabase(database=DATABASE_URL.database, host=DATABASE_URL.host, port=DATABASE_URL.port,
                               user=DATABASE_URL.username, password=DATABASE_URL.password)


class User(peewee.Model):
    user_id = peewee.IntegerField(verbose_name='User ID', unique=True)
    username = peewee.CharField(
        verbose_name='Username', max_length=128, null=True)
    first_name = peewee.CharField(
        verbose_name='First name', max_length=128, null=True)

    @classmethod
    def change_or_create(cls, user_id: int, username: str, first_name: str):
        user = User.select().where(User.user_id == user_id).first()
        if not user:
            return User(user_id=user_id, username=username, first_name=first_name)
        elif user and (user.username != username or user.first_name != first_name):
            user.username = username
            user.first_name = first_name
            return user
        else:
            return user

    def __str__(self):
        return f'First name – {self.first_name}, User ID – {self.user_id}, Username – {self.username}'

    class Meta:
        db_table = "users"
        database = DB


class Movie(peewee.Model):
    movie_id = peewee.AutoField(verbose_name='Идентификатор фильма/сериала')
    title = peewee.CharField(verbose_name='Название', max_length=140)
    release_year = peewee.IntegerField(verbose_name='Год производства')
    genre = peewee.CharField(verbose_name='Жанр', max_length=64)
    country = peewee.CharField(verbose_name='Страна', max_length=64)
    score = peewee.CharField(verbose_name='Оценка', max_length=3)
    season = peewee.IntegerField(verbose_name='Сезон', null=True)
    is_series = peewee.BooleanField(verbose_name='Сериал')
    cover = peewee.CharField(verbose_name='Ссылка на обложку', max_length=128)
    kinopoisk = peewee.CharField(verbose_name='Ссылка на КиноПоиск', max_length=128)

    @classmethod
    def from_kinopoisk(cls, kinopoisk, season=None):
        r = requests.get(kinopoisk)
        soup = BS(r.text, 'lxml')
        is_series = 'series' in kinopoisk
        title = soup.select_one('.styles_title__3tVSa').h1.span.text if is_series else soup.select_one(
            '.styles_title__2l0HH').text[:(soup.select_one('.styles_title__2l0HH').text.rindex('(') - 1)]
        table = list(soup.select_one('[data-test-id="encyclopedic-table"]').children)
        release_year = int(table[0].a.text)
        country = list(table[1].children)[1].text
        genre = list(table[2].children)[1].div.text
        score = soup.select_one('.film-rating-value').text
        try:
            cover = soup.select_one('img.film-poster').attrs['srcset'].split('//')[2].split(' ')[0]
        except:
            cover = soup.select_one('img.film-poster').attrs['src'][2:]
        return Movie(title=title, release_year=release_year, genre=genre, country=country, score=score, season=season,
                     is_series=is_series, cover=cover, kinopoisk=kinopoisk)

    def to_message(self):
        return f'🎞 {self.title}{f" ({self.season} сезон)" if self.is_series else ""}, <i>{self.release_year}</i>\n\nОценка: <i>{self.score}</i>\nЖанр: <i>{self.genre}</i>\nСтрана производства: <i>{self.country}</i>'

    def to_videos(self):
        return Video.select().where(Video.movie == self)

    def to_key(self):
        return f'📼 {self.title}' + (f': {self.season} сезон' if self.is_series and self.season else '')

    def __str__(self):
        return f'{"Сериал" if self.is_series else "Фильм"} {self.title}, {self.release_year}'

    class Meta:
        db_table = "movies"
        database = DB


class Video(peewee.Model):
    video_id = peewee.AutoField(verbose_name='Идентификатор видео')
    movie = peewee.ForeignKeyField(verbose_name='Контент', model=Movie)
    file_id = peewee.CharField(verbose_name='Идентификатор файла', max_length=128)
    number = peewee.IntegerField(verbose_name='Номер серии', null=True)
    title = peewee.CharField(verbose_name='Название', max_length=64, null=True)

    @classmethod
    def from_movie(cls, movie_id, file_id, number=None, title=None):
        movie = Movie.select().where(Movie.movie_id == movie_id).first()
        if movie:
            return Video(movie=movie, file_id=file_id, number=(
                movie.to_videos()[-1].number + 1 if movie.to_videos() else 1) if not number else number,
                         title=title) if movie.is_series else Video(movie=movie, file_id=file_id)

    @classmethod
    def delete_by_video_id(cls, video_id):
        video = Video.select().where(Video.video_id == video_id).first()
        return video.delete_instance() if video else None

    def to_message(self):
        return f'📼 {self.movie.title}' + (
            f': {self.movie.season} сезон {self.number} серия' if self.movie.is_series else '') + (
                   f'\n {self.title}' if self.title else '')

    def to_key(self):
        return f'📼 {self.movie.title}' + (
            f': {self.movie.season} сезон {self.number} серия' if self.movie.is_series else '')

    def __str__(self):
        return f'{self.movie}, {self.number} серия'

    class Meta:
        db_table = "videos"
        database = DB
        order_by = ('number',)


User.create_table()
Movie.create_table()
Video.create_table()
