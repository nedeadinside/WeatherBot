from aiogram.contrib.fsm_storage.memory import MemoryStorage
from app import register_state_handlers, BOT_TOKEN
from aiogram import executor, Dispatcher, Bot
import logging


bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


register_state_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
