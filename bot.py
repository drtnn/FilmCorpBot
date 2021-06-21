import config
from telebot import TeleBot
import upload_video

bot = TeleBot(token=config.TOKEN)

if __name__ == '__main__':
    from handlers import *
    upload_video.infinite_loop.start()
    bot.send_message(config.ADMIN[0], 'polling restart')
    bot.infinity_polling(timeout=5)
