from dotenv import load_dotenv
import os
import sqlalchemy

load_dotenv()
ADMIN = [int(user_id) for user_id in os.getenv('ADMIN').split(',')]
TOKEN = os.getenv('BOT_TOKEN')
BOTNAME = 'FilmCorpBot'
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')

CURRENTDIR = os.getenv('CURRENTDIR') if os.getenv('CURRENTDIR') else f'{os.getcwd()}/'
DOWNLOADDIR = CURRENTDIR + 'download/'
SESSIONDIR = CURRENTDIR + 'session/'

LOGFILE = CURRENTDIR + f'{BOTNAME.lower().replace("bot", "")}.log'
QUEUEFILE = DOWNLOADDIR + 'download_queue.json'

DATABASE_URL = sqlalchemy.engine.url.make_url(os.getenv('DATABASE_URL'))
