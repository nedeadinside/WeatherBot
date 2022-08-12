from aiogram.dispatcher.filters.state import State, StatesGroup
from config import BOT_TOKEN, db_name, WEATHER_API_KEY
from request import get_location, get_weather
from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from db import Database
import datetime


db = Database(db_name)
bot = Bot(BOT_TOKEN)


def time_check(user_time):
    hours = int(user_time[:2])
    minutes = int(user_time[3:])

    time = datetime.time(hours, minutes)
    start = datetime.time(0, 0)
    end = datetime.time(23, 59)
    return start <= time <= end


class Menu(StatesGroup):
    menu_state = State()
    finish_state = State()


class ChangeLocation(StatesGroup):
    get_city = State()


class ChangeTime(StatesGroup):
    get_time = State()


def db_write(uid, user_state):
    if db.user_exist(user_id=uid) is True:
        db.delete_user(user_id=uid)
        db.create_user(user_id=uid, user_info=user_state)
    else:
        db.create_user(user_id=uid, user_info=user_state)


async def start_state(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = types.KeyboardButton('Отправить мою геолокацию', request_location=True)
    keyboard.add(buttons)
    await message.answer('Введи пожалуйста свой город\nМожешь отправить геолокацию по кнопке', reply_markup=keyboard)
    await Menu.menu_state.set()


async def user_location(message: types.Message, state: FSMContext):
    city = get_location(message.text)
    if city is None:
        await message.answer('Не могу найти такой город, попробуй еще раз :(')
        return
    else:
        latitude, longitude = city

    markup = types.ReplyKeyboardRemove()
    await message.answer(
        'Отлично, теперь давай определимся с временем, когда я буду отправлять тебе погоду.\n\n' +
        'Отправь время по МСК в 24 часовом формате: hh:mm',
        reply_markup=markup
    )

    await state.update_data(lat=latitude, lon=longitude)
    await Menu.next()


async def user_location_button(message: types.Location, state: FSMContext):
    await state.update_data(lat=message['location']['latitude'], lon=message['location']['longitude'])
    await Menu.next()

    user_id = message['chat']['id']
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(
        chat_id=user_id,
        text='Отлично, теперь давай определимся с временем, когда я буду отправлять тебе погоду.\n\n' +
        'Отправь время по МСК в 24 часовом формате: hh:mm',
        reply_markup=markup
    )


async def finish_state(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()
    try:
        if time_check(message.text) is True:
            await state.update_data(time=message.text)

            state_data = await state.get_data()
            await state.finish()

            db_write(uid=message.from_user.id, user_state=state_data)

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Посмотреть погоду', 'Изменить город', 'Изменить время']
            keyboard.add(*buttons)
            await message.answer(
                'Я сохранил время, теперь каждый день тебе будет отправляться прогноз погоды :)',
                reply_markup=keyboard
                )

        else:
            await message.answer('Вы ввели некорректное время!', reply_markup=markup)
            return

    except Exception as e:
        print(e)
        await message.answer('Вы ввели некорректное время!', reply_markup=markup)
        return


async def get_location_state(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = types.KeyboardButton('Отправить мою геолокацию', request_location=True)
    keyboard.add(buttons)
    await message.answer('Введи пожалуйста свой город\nМожешь отправить геолокацию по кнопке', reply_markup=keyboard)
    await ChangeLocation.get_city.set()


async def get_location_state_finish(message: types.Message, state: FSMContext):
    city = get_location(message.text)
    if city is None:
        await message.answer('Не могу найти такой город, попробуй еще раз :(')
        return
    else:
        latitude, longitude = city

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Посмотреть погоду', 'Изменить город', 'Изменить время']
    keyboard.add(*buttons)
    await message.answer('Локация изменена!', reply_markup=keyboard)

    await state.update_data(lat=latitude, lon=longitude)
    data = await state.get_data()
    db.rewrite_location(message.from_user.id, data['lat'], data['lon'])
    await state.finish()


async def get_location_state_button(message: types.Location, state: FSMContext):
    await state.update_data(lat=message['location']['latitude'], lon=message['location']['longitude'])
    data = await state.get_data()
    await state.finish()

    user_id = message['chat']['id']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Посмотреть погоду', 'Изменить город', 'Изменить время']
    keyboard.add(*buttons)
    db.rewrite_location(user_id, data['lat'], data['lon'])
    await bot.send_message(chat_id=user_id, text='Локация изменена!', reply_markup=keyboard)


async def change_time_state(message: types.Message):
    markup = types.ReplyKeyboardRemove()
    await message.answer('Давай определимся с временем, когда я буду отправлять тебе погоду.\n\n' +
                         'Отправь время по МСК в 24 часовом формате: hh:mm', reply_markup=markup)
    await ChangeTime.get_time.set()


async def finish_change_time(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()
    try:
        if time_check(message.text) is True:
            await state.update_data(time=message.text)

            state_data = await state.get_data()
            await state.finish()

            db.rewrite_time(user_id=message.from_user.id, time=state_data['time'])

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Посмотреть погоду', 'Изменить город', 'Изменить время']
            keyboard.add(*buttons)
            await message.answer('Я сохранил время:)', reply_markup=keyboard)

        else:
            await message.answer('Вы ввели некорректное время!', reply_markup=markup)
            return

    except Exception as e:
        print(e)
        await message.answer('Вы ввели некорректное время!', reply_markup=markup)
        return


async def commands_cathc(message: types.Message):
    commands = ['Посмотреть погоду', 'Изменить город', 'Изменить время']
    if message.text in commands:
        if message.text == commands[0]:
            data = db.get_user_info(message.from_user.id)

            await message.answer('Вот прогноз погоды на сегодня:')
            await message.answer(get_weather(data['latitude'], data['longitude'], api_key=WEATHER_API_KEY))
        elif message.text == commands[1]:
            await get_location_state(message)
        else:
            await change_time_state(message)
    else:
        await message.answer('Я не понял тебя, пожалуйста воспользуйся кнопками для ответа!')


async def hello(message: types.Message):
    if db.user_exist(message.from_user.id) is True:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['Посмотреть погоду', 'Изменить город', 'Изменить время']
        keyboard.add(*buttons)
        await message.answer('Воспользуйся кнопками, чтобы посмотреть интересующую информацию', reply_markup=keyboard)
    else:
        await message.answer('Привет, запускаю стейт')
        await start_state(message)


def register_state_handlers(dp: Dispatcher):
    dp.register_message_handler(hello, commands='start')
    dp.register_message_handler(commands_cathc)

    dp.register_message_handler(get_location_state, state='*', commands='resetlocation')
    dp.register_message_handler(get_location_state_finish, state=ChangeLocation.get_city)
    dp.register_message_handler(get_location_state_button, state=ChangeLocation.get_city, content_types=['location'])

    dp.register_message_handler(change_time_state, state='*', commands='resettime')
    dp.register_message_handler(finish_change_time, state=ChangeTime.get_time)

    dp.register_message_handler(start_state, state='*', commands='resetsettings')
    dp.register_message_handler(user_location, state=Menu.menu_state)
    dp.register_message_handler(user_location_button, state=Menu.menu_state, content_types=['location'])
    dp.register_message_handler(finish_state, state=Menu.finish_state)
