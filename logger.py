import config
import logging
import os
import telebot

if os.path.exists(config.LOGFILE):
    file = open(config.LOGFILE, 'a')  # Создание файла, если он отсутствовал
    file.close()

logging.basicConfig(filename=config.LOGFILE,
                    format='[%(asctime)s] [%(levelname)s] => %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
telebot.logger.setLevel(logging.ERROR)
logging.getLogger('telethon').setLevel(level=logging.ERROR)
