import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

import requests
import json

from message_handlers import generate_deadlines, generate_descr, deleted_deadline

class vk_user:
    """
    Класс пользователя бота. Все взаимодействие с ним проимсодит через этот класс
    Методы:
    position() - возвращает/изменяет позицию пользователя в меню
    users() - добавляет нового пользователя/получает всех пользователей
    deadlines_get() - получает список дедлайнов
    mark_done() - отмечает дедлайны выполненными
    """

    def __init__(self, vk_userID=-1):
        """
        При инициализации без указания vk_userID, берется по умолчанию -1. Нужен для идентификации пользователя
        vk_userID - id пользователя обрабатываемого ботом на данный момент
        """
        self.__vk_userID = vk_userID

    @property
    def position(self) -> str:
        """
        Getter позиции пользователя, возвращает строку с его текущей позицией
        return - возвращает строку с позицией пользователя в меню бота
        """
        return requests.get('http://127.0.0.1:5000/api/user_position',
                            json={'uid_type': 'vk', 'uid': self.__vk_userID}).text

    @position.setter
    def position(self, user_position: str):
        """
        Setter позиции пользователя, отправляет API новую позицию в меню пользователя
        user_position - позиция пользователя в меню
        """
        requests.put('http://127.0.0.1:5000/api', params={'type_of_action': 'new_pos'},
                     json={'uid_type': 'vk', 'uid': self.__vk_userID, 'new_pos': user_position})

    def deadlines_get(self, deadline_type: str) -> list:
        """
        Метод для получения текущего или просроченного дедлайна пользователя, возвращает все дедлайны в виде списка
        deadline_type - тип дедлайна(просроченный, текущий)
        """
        return json.loads(requests.get('http://127.0.0.1:5000/api/{}'.format(deadline_type),
                                       json={'uid_type': 'vk', 'uid': self.__vk_userID}).text)

    def mark_done(self, description: list):
        """
        Метод для отметки сделанного дедлайна
        description - название дедлайна(ов) для отметки
        """
        requests.put('http://127.0.0.1:5000/api', params={'type_of_action': 'deadline_done'},
                     json={'uid_type': 'vk', 'uid': self.__vk_userID, 'what_del': description})

    @property
    def users(self) -> list:
        """
        Getter списка пользователей пользующихся ботом, возвращает список пользователей
        """
        return json.loads(requests.get('http://127.0.0.1:5000/api/get_users',
                                       json={'uid_type': 'vk', 'uid': self.__vk_userID}).text)

    @users.setter
    def users(self, new_user):
        """
        Setter списка пользователей. Добавляет нового пользователя в бота
        """
        requests.post('http://127.0.0.1:5000/api', params={'type_of_action': 'add_user'},
                      json={'uid_type': 'vk', 'uid': new_user})


def write_message_keyboard(sender: str,
                           buttons: list,
                           but_place: list,
                           message: str = None,
                           type_button: bool = True):
    """
    Функция для создания и отправки клавиатуры.
    sender: ID пользователя.
    buttons: Список надписей на кнопках в формате [Кнопка1, Кнопка2]
    but_place: Расположение кнопок на экране, а так же их цвет в формате [['Цвет кнопки','Цвет кнопки'],\
    [2 строка(аналогично 1)]]
    message: Что бот выведет в ответ
    type_button: Тип кнопок. Исчезающие после нажатия/сообщения - True, исчезающие после появления новой клавиатуры - False
    """
    keyboard = VkKeyboard(one_time=type_button)
    counter = 0  # Счетчик сообщений, задается 1 раз в начале функции

    for j in range(len(but_place)):

        for button_color in but_place[j]:  # Перебор кнопок согласно их позициям, цвету и надписям на них

            if button_color == 'WHITE':
                keyboard.add_button(buttons[counter], color=VkKeyboardColor.SECONDARY)

            elif button_color == 'RED':
                keyboard.add_button(buttons[counter], color=VkKeyboardColor.NEGATIVE)

            elif button_color == 'GREEN':
                keyboard.add_button(buttons[counter], color=VkKeyboardColor.POSITIVE)

            elif button_color == 'BLUE':
                keyboard.add_button(buttons[counter], color=VkKeyboardColor.PRIMARY)

            counter += 1

        if j != len(but_place) - 1:
            keyboard.add_line()

    vk.messages.send(peer_id=sender,
                     random_id=get_random_id(),
                     keyboard=keyboard.get_keyboard(),
                     message=message)


def mainLoop():
    """
    Основная функция-цикл отвечающая за прослушивание LongPoll событий
    global vk - метод VK API. Позволяет взаимодействовать с
    """
    with open('api_vk.txt', 'r') as API_KEYS:
        TOKEN = API_KEYS.readline()
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkLongPoll(vk_session)
    global vk
    vk = vk_session.get_api()
    user_temp = vk_user()
    current_users = user_temp.users
    for event in longpoll.listen():
        print(event.type)
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_data = vk_user(event.user_id)
            if event.user_id not in current_users:
                vk_user().users = int(event.user_id)
                write_message_keyboard(event.user_id, ['Текущие дедлайны', 'Просроченные дедлайны'], [['WHITE', 'RED']],
                                       'Выберите из предложенного:')
                current_users.append(int(event.user_id))
            else:
                user_message_handler(user_data, event)


def user_message_handler(user_data: vk_user, event):
    """
    Обработчик сообщений пользователя
    user_data - объект класса vk_user
    event - событие VKLongPoll
    """
    user_position = user_data.position
    print(user_position)
    if user_position == 'Main' and event.message.lower() in ['текущие дедлайны', 'просроченные дедлайны']:
        write_message_keyboard(event.user_id, ['Назад'], [['RED']],
                               generate_deadlines(user_data.deadlines_get(
                                   'Current' if event.message.lower() == 'текущие дедлайны' else 'Overdue'),
                                   event.message.lower(), 'vk'))

        if event.message.lower() == 'текущие дедлайны':
            user_data.position = 'Current'

        else:
            user_data.position = 'Overdue'

    elif user_position in ['Current', 'Overdue'] and '/done' in event.message.lower()[:5] or\
            '/выполнено' in event.message.lower()[0:10]:
        try:
            descr_list = generate_descr(event.message.lower().split()[1:], user_data.deadlines_get(user_position))
            user_data.mark_done(descr_list)
            write_message_keyboard(event.user_id, ['Текущие дедлайны', 'Просроченные дедлайны'], [['WHITE', 'RED']],
                                   deleted_deadline(descr_list))
            user_data.position = 'Main'

        except:
            write_message_keyboard(event.user_id, ['Назад'], [['RED']], 'Ошибка, введите "Назад", чтобы отметить '
                                                                        'выполненными некоторые элементы, введите'
                                                                        ' /done [номер(a) элеманта(ов)] или /выполнено'
                                                                        ' [номер(a) элеманта(ов)]. Например: '
                                                                        '/done 1 2 4')

    elif user_position in ['Current', 'Overdue'] and event.message.lower() == 'назад':
        write_message_keyboard(event.user_id, ['Текущие дедлайны', 'Просроченные дедлайны'], [['WHITE', 'RED']],
                               'Выберите из предложенного:')
        user_data.position = 'Main'

    else:
        if user_position in ['Current', 'Overdue']:
            write_message_keyboard(event.user_id, ['Назад'], [['RED']], 'Ошибка, введите "Назад", чтобы отметить '
                                                                        'выполненными некоторые элементы, введите'
                                                                        ' /done [номер(a) элеманта(ов)] или /выполнено'
                                                                        ' [номер(a) элеманта(ов)]. Например: '
                                                                        '/done 1 2 4')
        else:
            write_message_keyboard(event.user_id, ['Текущие дедлайны', 'Просроченные дедлайны'], [['WHITE', 'RED']],
                                   'Ошибка, выберите из предложенного:')


if __name__ == '__main__':
    mainLoop()
