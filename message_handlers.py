def generate_deadlines(schedule: list, deadline_type: str, vk_or_tg) -> str:
    """
    Функция генерирующая сообщения дедлайнов
    :schedule: список ВСЕХ дедлайнов
    :deadline_type: строка с типом дедлайна Current/Overdue
    :return: возвращает сообщение для отправки пользователю
    """
    message_to_user = '{}:\n'.format(deadline_type[0].upper() + deadline_type[1:].lower()) if vk_or_tg == 'vk' else\
        ''
    counter = 0
    for date in schedule:
        message_to_user += generate_message_to_user(schedule[counter], counter)
        counter += 1

    message_to_user += 'Что бы отметить выполненными некоторые элементы, введите /done [номер(a) элеманта(ов)] ' \
                       'или /выполнено [номер(a) элеманта(ов)]'if vk_or_tg == 'vk' else\
        'Что бы отметить выполненными некоторые элементы, введите /done [current/overdue]' \
        ' [номер(a) элеманта(ов)]'
    return message_to_user


def generate_message_to_user(schedule_point: list, counter: int) -> str:
    """
    Функция генерирующая промежуточное сообщение для пользователя
    :schedule_point: список с параметрами расписания
    :counter: счетчик строки
    :return: возвращает элемент списка в сообщение возвращаемом пользователю
    """
    return '{}. {}. Дата: {}, время: {}\n'.format(counter + 1, schedule_point[2],
                                                  schedule_point[0],
                                                  schedule_point[1]
                                                  )


def generate_descr(what_del: list, deadline_data: list) -> list:
    """
    Функция генерирующая список на отметку дедлайна
    :what_del: список номеров пунктов на отметку
    :deadline_data: список дедлайнов, [('12.12.2021', '12:20', 'math')]
    :return: возвращает список дедлайнов для удаления
    """
    output_d = []
    for i in what_del:
        output_d.append(deadline_data[int(i) - 1][2])
    return output_d


def deleted_deadline(descr_list: list) -> str:
    """
    Функция генератор сообщения об успешной отметке дедлайнов
    :descr_list: отмеченные дедлайны, [['math']]
    :return: возвращает строку с информацией об отмеченных дедлайнах
    """
    output = 'Следующие дедлайны были удалены:\n'
    counter = 1
    for i in descr_list:
        output += '{}. {}\n'.format(str(counter), i)
        counter += 1
    output += 'Выберите из предложенного:'
    return output
