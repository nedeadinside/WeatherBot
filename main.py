from aiogram.contrib.fsm_storage.memory import MemoryStorage
from app import register_state_handlers, db, bot
from aiogram import executor, Dispatcher
from config import WEATHER_API_KEY
from request import get_weather
import aioschedule
import datetime
import logging
import asyncio


dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
register_state_handlers(dp)


async def get_datetime():
    msk_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    msk_time = '{:02d}:{:02d}'.format(msk_time.hour, msk_time.minute)
    users = db.get_time(msk_time)
    for user in users:
        await bot.send_message(chat_id=user['user_id'], text='Привет! Прогноз погоды на сегодня:')
        await bot.send_message(chat_id=user['user_id'], text=get_weather(
            latitude=user['latitude'],
            longitude=user['longitude'],
            api_key=WEATHER_API_KEY
        ))


async def scheduler():
    aioschedule.every(60).seconds.do(get_datetime)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp: Dispatcher):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
