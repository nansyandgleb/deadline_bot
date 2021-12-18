import unittest
import app

class get_user_position(unittest.TestCase):
    def test_get_user_position_overdue(self):
        self.assertEqual(app.get_user_position('vk', 87654321), 'Overdue')
        self.assertEqual(app.get_user_position('tg', 456), 'Overdue')

    def test_get_user_position_main(self):
        self.assertEqual(app.get_user_position('vk', 123), 'Main')
        self.assertEqual(app.get_user_position('tg', 789), 'Main')

    def test_get_user_position_current(self):
        self.assertEqual(app.get_user_position('vk', 12345678), 'Current')
        self.assertEqual(app.get_user_position('tg', 456789), 'Current')


class get_users(unittest.TestCase):
    def test_get_users_vk(self):
        self.assertEqual(app.get_users('vk'), [123, 1234, 12345, 12345678, 87654321])
        self.assertEqual(app.get_users('tg'), [456, 789, 44444, 456789, 987654])

class get_schedule(unittest.TestCase):
    def test_get_schedule_current_one_F(self):
        self.assertEqual(app.get_schedule([0], [('12.12.2022', '12:20', 'Math')], 'Current'),
                         [('12.12.2022', '12:20', 'Math')])
        self.assertEqual(app.get_schedule([0], [('12.12.2022', '12:20', 'Math')], 'Current'),
                         [('12.12.2022', '12:20', 'Math')])
    def test_get_schedule_current_one_T(self):
        self.assertEqual(app.get_schedule([1], [('12.12.2022', '12:20', 'Math')], 'Current'), [])

    def test_get_schedule_current_few_random(self):
        self.assertEqual(app.get_schedule([0, 1, 0], [('12.12.2022', '12:20', 'Math1'),('12.12.2022', '12:20', 'Math2'),
                                                      ('12.12.2022', '12:20', 'Math3')], 'Current'),
                                          [('12.12.2022', '12:20', 'Math1'), ('12.12.2022', '12:20', 'Math3')])

    def test_get_schedule_current_few_0_but_1_overdue(self):
        self.assertEqual(app.get_schedule([0, 0, 0], [('12.12.2022', '12:20', 'Math1'),('12.12.2020', '12:20', 'Math2'),
                                                      ('12.12.2022', '12:20', 'Math3')], 'Current'),
                                          [('12.12.2022', '12:20', 'Math1'), ('12.12.2022', '12:20', 'Math3')])
    def test_get_schedule_overdue_one_F(self):
        self.assertEqual(app.get_schedule([0], [('12.12.2020', '12:20', 'Math')], 'Overdue'), [('12.12.2020', '12:20', 'Math')])

    def test_get_schedule_overdue_one_T(self):
        self.assertEqual(app.get_schedule([1], [('12.12.2020', '12:20', 'Math')], 'Overdue'), [])

    def test_get_schedule_ovedue_few_random(self):
        self.assertEqual(app.get_schedule([0, 1, 0], [('12.12.2020', '12:20', 'Math1'),('12.12.2020', '12:20', 'Math2'),
                                                      ('12.12.2020', '12:20', 'Math3')], 'Overdue'),
                                          [('12.12.2020', '12:20', 'Math1'), ('12.12.2020', '12:20', 'Math3')])

    def test_get_schedule_overdue_few_0_but_1_current(self):
        self.assertEqual(app.get_schedule([0, 0, 0], [('12.12.2020', '12:20', 'Math1'), ('12.12.2022', '12:20', 'Math2'),
                                                      ('12.12.2020', '12:20', 'Math3')], 'Overdue'),
                                          [('12.12.2020', '12:20', 'Math1'), ('12.12.2020', '12:20', 'Math3')])

class add_deadline(unittest.TestCase):
    def test_add_deadline(self):
        self.assertEqual(app.add_deadline({'date': '22.12.2021', 'time': "12:20", "description": "Math121"}), 'Done')

class change_new_position(unittest.TestCase):
    def test_change_position_overdue(self):
        self.assertEqual(app.change_new_position({'uid_type': 'vk', 'uid': 1234, 'new_pos': 'Overdue'}), 'Done')
        self.assertEqual(app.change_new_position({'uid_type': 'tg', 'uid': 987654, 'new_pos': 'Overdue'}), 'Done')

    def test_change_main(self):
        self.assertEqual(app.change_new_position({'uid_type': 'vk', 'uid': 1234, 'new_pos': 'Main'}), 'Done')
        self.assertEqual(app.change_new_position({'uid_type': 'tg', 'uid': 987654, 'new_pos': 'Main'}), 'Done')

    def test_change_current(self):
        self.assertEqual(app.change_new_position({'uid_type': 'vk', 'uid': 1234, 'new_pos': 'Current'}), 'Done')
        self.assertEqual(app.change_new_position({'uid_type': 'tg', 'uid': 987654, 'new_pos': 'Current'}), 'Done')


class mark_deadline_done(unittest.TestCase):
    def test_mark_deadline_done_one(self):
        self.assertEqual(app.mark_deadline_done({'uid_type': 'vk', 'uid': 1234, 'what_del': ['Math1']}), 'Done')
        self.assertEqual(app.mark_deadline_done({'uid_type': 'tg', 'uid': 1234, 'what_del': ['Math1']}), 'Done')

    def test_mark_deadline_done_many(self):
        self.assertEqual(app.mark_deadline_done({'uid_type': 'vk', 'uid': 12345, 'what_del': ['Math1', 'Math2']}), 'Done')
        self.assertEqual(app.mark_deadline_done({'uid_type': 'tg', 'uid': 12345, 'what_del': ['Math1', 'Math2']}), 'Done')

if __name__ == '__main__':
    unittest.main()
