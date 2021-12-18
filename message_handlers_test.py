import unittest
import message_handlers


class generate_deadlines(unittest.TestCase):
    def test_generate_deadlines_one_vk(self):
        self.assertEqual(
            message_handlers.generate_deadlines([['12.12.2021', '12:20', 'Math']], 'Просроченные дедлайны', 'vk'),
            'Просроченные дедлайны:\n1. Math. Дата: 12.12.2021, время: 12:20\nЧто бы отметить'
            ' выполненными некоторые элементы, введите /done [номер(a) элеманта(ов)] или'
            ' /выполнено [номер(a) элеманта(ов)]')

    def test_generate_deadlines_few_vk(self):
        self.assertEqual(
            message_handlers.generate_deadlines([['12.12.2021', '12:20', 'Math'], ['12.12.2021', '12:20', 'Math2']],
                                                'Текущие дедлайны', 'vk'),
            'Текущие дедлайны:\n1. Math. Дата: 12.12.2021, время: 12:20'
            '\n2. Math2. Дата: 12.12.2021, время: 12:20\nЧто бы отметить выполненными '
            'некоторые элементы, введите /done [номер(a) элеманта(ов)] или'
            ' /выполнено [номер(a) элеманта(ов)]')

    def test_generate_deadlines_one_tg(self):
        self.assertEqual(
            message_handlers.generate_deadlines([['12.12.2021', '12:20', 'Math']], 'Просроченные дедлайны', 'tg'),
            '1. Math. Дата: 12.12.2021, время: 12:20\nЧто бы отметить '
            'выполненными некоторые элементы, введите /done [current/overdue] [номер(a) элеманта(ов)]')

    def test_generate_deadlines_few_tg(self):
        self.assertEqual(
            message_handlers.generate_deadlines([['12.12.2021', '12:20', 'Math'], ['12.12.2021', '12:20', 'Math2']],
                                                'Текущие дедлайны', 'tg'),
            '1. Math. Дата: 12.12.2021, время: 12:20'
            '\n2. Math2. Дата: 12.12.2021, время: 12:20\nЧто бы отметить выполненными '
            'некоторые элементы, введите /done [current/overdue] [номер(a) элеманта(ов)]')


class generate_message_to_user(unittest.TestCase):
    def test_generate_message_to_user(self):
        self.assertEqual(message_handlers.generate_message_to_user(['12.12.2021', '12:20', 'Math'], 0),
                         '1. Math. Дата: 12.12.2021, время: 12:20\n')

    def test_generate_message_to_user_rus(self):
        self.assertEqual(message_handlers.generate_message_to_user(['12.12.2021', '12:20', 'Матем'], 0),
                         '1. Матем. Дата: 12.12.2021, время: 12:20\n')


class generate_descr(unittest.TestCase):
    def test_generate_descr_one(self):
        self.assertEqual(
            message_handlers.generate_descr(['1'], [('12.12.2020', '12:20', 'Math1'), ('12.12.2022', '12:20', 'Math2'),
                                                    ('12.12.2020', '12:20', 'Math3')]), ['Math1'])

    def test_generate_descr_few(self):
        self.assertEqual(message_handlers.generate_descr(['1', '3'], [('12.12.2020', '12:20', 'Math1'),
                                                                      ('12.12.2022', '12:20', 'Math2'),
                                                                      ('12.12.2020', '12:20', 'Math3')]),
                         ['Math1', 'Math3'])

    def test_generate_descr_all(self):
        self.assertEqual(message_handlers.generate_descr(['1', '3', '2'], [('12.12.2020', '12:20', 'Math1'),
                                                                           ('12.12.2022', '12:20', 'Math2'),
                                                                           ('12.12.2020', '12:20', 'Math3')]),
                         ['Math1', 'Math3', 'Math2'])


class deleted_deadline(unittest.TestCase):
    def test_deleted_deadline_few(self):
        self.assertEqual(message_handlers.deleted_deadline(['Math1', 'Math3', 'Math2']),
                         'Следующие дедлайны были удалены:\n1. Math1\n2. Math3\n3. Math2\nВыберите из предложенного:')

    def test_deleted_deadline_one(self):
        self.assertEqual(message_handlers.deleted_deadline(['Math1']),
                         'Следующие дедлайны были удалены:\n1. Math1\nВыберите из предложенного:')


if __name__ == '__main__':
    unittest.main()
