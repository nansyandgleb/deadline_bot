import asyncio
import os
import random
import json
import requests
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from message_handlers import generate_message_to_user, generate_deadlines, deleted_deadline, generate_descr

with open('api_tg.txt', 'r') as API_KEYS:
    TOKEN = API_KEYS.readline()

bot = Bot(token=TOKEN)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)


class user_tg:
    """
    Класс user_tg отвечает за взаимодействие пользователя бота с API
    Методы
    -------
    :user(): получает/изменяет список пользователей
    :get_deadline: получает список дедлайнов
    :mark_deadline: отмечает дедлайны выполненными
    """
    def __init__(self, tg_userid=-1):
        """
        Инициализатор, необходим для идентификации пользователя
        :tg_userid: - уникальный ID пользователя телеграм
        """
        self.__tg_userid = tg_userid

    @property
    def user(self) -> list:
        """
        Фкнкция-getter, возвращает всех пользователей телеграм с помощью API
        :return: возвращает список пользователей [uid1, uid2,..., uidn]
        """
        return json.loads(requests.get('http://127.0.0.1:5000/api/get_users',
                                       json={'uid_type': 'tg', 'uid': self.__tg_userid}).text)

    @user.setter
    def user(self, tg_uid: any):
        """
        Функция-setter, отсылает нового пользователя в API
        :tg_uid: - уникальный ID пользователя телеграм
        """
        requests.post('http://127.0.0.1:5000/api', params={'type_of_action': 'add_user'},
                      json={'uid_type': 'tg', 'uid': tg_uid})

    def get_deadline(self, deadline_type: str) -> list:
        """
        Функция возвращает список дедлайнов
        :deadline_type: тип дедлайна
        :return: возвращает список вида [[date, time, description]]
        """
        return json.loads(requests.get('http://127.0.0.1:5000/api/{}'.format(deadline_type),
                                       json={'uid_type': 'tg', 'uid': self.__tg_userid}).text)

    def mark_deadline(self, description: str):
        """
        Функция отсылает в API описание выполненных дедлайнов
        :desrition: список с названиями дедлайнов вида [descr1, descr2]
        """
        requests.put('http://127.0.0.1:5000/api', params={'type_of_action': 'deadline_done'},
                     json={'uid_type': 'tg', 'uid': self.__tg_userid, 'what_del': description})


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    """
    Функция обработчик команды start. Запускается при инициализации бота пользователем
    :message: данные о сообщении TG
    """
    await message.answer("Приветствую пользователь, я бот дедлайнов",
                         reply_markup=ReplyKeyboardMarkup(
                             [
                                 [
                                     KeyboardButton(text="Текущие дедлайны"),
                                     KeyboardButton(text="Просроченные дедлайны ")
                                 ],
                                 [
                                     KeyboardButton(text="Получить мотивацию")
                                 ]
                             ],
                             resize_keyboard=True
                         ))
    user_tg().user = message.chat.id


@dp.message_handler(text="Просроченные дедлайны")
async def start(message: types.Message):
    """
         Функция обработчик команды Просроченные дедлайны. Запускается при нажатии на кнопку просроченные дедлайны.
         Отправляет пользователю просроченные дедлайны
         :message: данные о сообщении TG
    """
    user_data = user_tg(message.chat.id)
    await message.answer("Список дедлайнов просроченных:\n{}".format(generate_deadlines(user_data.get_deadline("Overdue"), "Overdue", "tg")),
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(text="Назад", callback_data="back")
                                 ]
                             ]
                         ))


@dp.message_handler(text="Текущие дедлайны")
async def start(message: types.Message):
    """
         Функция обработчик команды Текущие дедлайны. Запускается при нажатии на кнопку Текущие дедлайны.
         Отправляет пользователю текущие дедлайны
         :message: данные о сообщении TG
    """
    user_data = user_tg(message.chat.id)
    await message.answer("Список дедлайнов текущих:\n{}".format(generate_deadlines(user_data.get_deadline("Current"), "Current", "tg")),
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(text="Назад", callback_data="back")
                                 ]
                             ]
                         ))


@dp.message_handler(commands="done")
async def done_handler(message: types.Message):
    """
         Функция обработчик команды /done.
         Принимает от пользователя параметры после /done, например /done [current/overdue] [номер(а) дедлайнов для удаления)
         :message: данные о сообщении TG
    """
    user_data = user_tg(message.chat.id)
    try:
        type_of_deadline = message.text[6].upper() + message.text[7:13]
        deadlines = user_data.get_deadline(type_of_deadline)
        descr_list = generate_descr(message.text.split()[2:], deadlines)
        user_data.mark_deadline(descr_list)
        await message.answer(deleted_deadline(descr_list))
    except:
        await message.answer("Ошибка, введите повторно")



@dp.callback_query_handler(text="back", state="*")
async def get_back(call: types.CallbackQuery, state: FSMContext):
    """Функция обработчик команды back.
       Удаляет сообщение с дедлайнами
       :message: данные о сообщении TG
    """
    await call.answer(cache_time=10)

    await call.message.answer("Вы вернулись",
                              reply_markup=ReplyKeyboardMarkup(
                                  [
                                      [
                                          KeyboardButton(text="Текущие дедлайны"),
                                          KeyboardButton(text="Просроченные дедлайны")
                                      ]
                                  ],
                                  resize_keyboard=True
                              ))

    await call.message.delete()

    await state.finish()


async def fetch_users() -> list:
    """
    Вспомогательная функция для асинхронной отправки уведомлений, возвращает всех пользователей телеграм с помощью API
    :return: возвращает список пользователей [uid1, uid2,..., uidn]
    """
    return json.loads(requests.get('http://127.0.0.1:5000/api/get_users',
                                   json={'uid_type': 'tg'}).text)


async def fetch_deadlines(tg_id):
    """
        Вспомогательная функция для асинхронной отправки уведомлений, возвращает список дедлайнов
        :deadline_type: тип дедлайна
        :return: возвращает список вида [[date, time, description]]
    """
    return json.loads(requests.get('http://127.0.0.1:5000/api/Current', json={'uid_type': 'tg', 'uid': tg_id}).text)


async def deadline_task():
    """
    Задача для асинхронной отправки уведомлений о скором окончании дедлайнов. Отправляет пользовтаелю уведомления
    """
    prev_hour = 0
    while True:
        if prev_hour < datetime.datetime.now().time().hour:
            users = await fetch_users()
            s = ''
            for user in users:
                deadlines = await fetch_deadlines(user)
                time_now = datetime.datetime.now().time()
                for deadline in deadlines:
                    if (time_now.hour == int(deadline[1][0:2]) and
                            (datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                           day=int(deadline[0][:2])) == datetime.datetime.now().date() or
                             datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                           day=int(deadline[0][:2])) == (
                                     datetime.datetime.now() + datetime.timedelta(days=1)).date() or
                             datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                           day=int(deadline[0][:2])) == (
                                     datetime.datetime.now() + datetime.timedelta(days=3)).date() or
                             datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                           day=int(deadline[0][:2])) == (
                                     datetime.datetime.now() + datetime.timedelta(days=7)).date()
                            )):
                        await bot.send_message(chat_id=user, text='Скоро заканчивается дедлайн: {} {} {}'.format(
                            deadline[2], deadline[0], deadline[1]))
            prev_hour = datetime.datetime.now().time().hour
        await asyncio.sleep(600)

if __name__ == '__main__':
    from aiogram import executor

    loop = asyncio.get_event_loop()
    loop.create_task(deadline_task())

    executor.start_polling(dp)
