from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from request import get_location
from config import BOT_TOKEN
import datetime


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
            # СОХРАНИТЬ В БД ДАННЫЕ ИЗ СТЕЙТА
            await Menu.next()

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


async def hello(message: types.Message):
    await message.answer('Привет, запускаю стейт')
    await start_state(message)


def register_state_handlers(dp: Dispatcher):
    dp.register_message_handler(hello, commands='start')

    dp.register_message_handler(start_state, state='*', commands='resetsettings')
    dp.register_message_handler(user_location, state=Menu.menu_state)
    dp.register_message_handler(user_location_button, state=Menu.menu_state, content_types=['location'])
    dp.register_message_handler(finish_state, state=Menu.finish_state)
