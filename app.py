from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
import json
import datetime

if __name__ != '__main__':
    db_name = 'test.db'

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
else:
    db_name = 'main.db'

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)


class users(db.Model):
    """
    Класс таблиц SQLAlchemy, наследуется от класса db.Model. Используется для создания/взаимодействия с базой данных
    SQLite3
    uid - уникальный идентификатор записи в таблице
    vk_uid - уникальный идентификатор пользователя из VK
    tg_uid - кникальный идентификатор пользователя из TG
    user_position - позиция пользователя в меню бота
    """
    uid = db.Column(db.Integer, primary_key=True)
    vk_uid = db.Column(db.Integer)
    tg_uid = db.Column(db.Integer)
    user_position = db.Column(db.String)


class deadlines(db.Model):
    """
    Класс таблиц SQLAlchemy, наследуется от класса db.Model. Используется для создания/взаимодействия с базой данных
    SQLite3
    id - уникальный идентификатор записи в таблице
    date - дата окончания дедлайна
    time - время окончания дедлайна
    description - название дедлайна
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    time = db.Column(db.String)
    description = db.Column(db.String, unique=True)


@app.route('/api/user_position', methods=['GET'])
def get_handler_user_position():
    """
    Функция-обработчик входящего GET запроса по адресу '/api/user_position'
    return - возвращает строку с позицией пользователя
    """
    return get_user_position(request.json['uid_type'], request.json['uid'])


def get_user_position(type_uid: str, id: any) -> str:
    """
    Функция получает на вход ID пользователя, отдает позицию пользователя в меню бота
    type_uid - тип ID tg/vk
    id - id пользователя
    return - возвращает строку с позицей пользователя
    """
    if type_uid == 'vk':
        resp = users.query.filter_by(vk_uid=id).one()
    else:
        resp = users.query.filter_by(tg_uid=id).one()
    return resp.user_position


@app.route('/api/get_users', methods=['GET'])
def get_handler_users():
    """
    Функция-обработчик входящего GET запроса по адресу '/api/get_users'
    return - возвращает json с пользователями
    """
    return json.dumps(get_users(request.json['uid_type']))


def get_users(type_uid) -> list:
    """
    Функция запрашивает из БД все VK/TG ID пользователей
    return - возвращает список uid пользователей
    """
    if type_uid == 'vk':
        resp = users.query.with_entities(users.vk_uid).all()
    else:
        resp = users.query.with_entities(users.tg_uid).all()
    output = []
    for i in resp:
        if i[0] != None and i[0] != '':
            output.append(i[0])
    return output


@app.route('/api/Current', methods=['GET'])
def get_handler_current_schedule():
    """
    Функция-обработчик входящего GET запроса по адресу '/api/Current'
    return - возвращает json с актуальными дедлайнами
    """
    if request.json['uid_type'] == 'vk':
        output_TF = [
            *db.engine.execute("SELECT * from users where vk_uid = {}".format(request.json['uid'])).fetchone()[4:]]
    else:
        output_TF = [
            *db.engine.execute("SELECT * from users where tg_uid = '{}'".format(request.json['uid'])).fetchone()[4:]]
    buffer = db.engine.execute("SELECT date, time, description FROM deadlines").fetchall()
    return json.dumps(list(map(list, get_schedule(output_TF, buffer, 'Current'))))


@app.route('/api/Overdue', methods=['GET'])
def get_handler_overdue_schedule():
    """
    Функция-обработчик входящего GET запроса по адресу '/api/Overdue'
    return - возвращает json с просроченными дедлайнами
    """
    if request.json['uid_type'] == 'vk':
        output_TF = [
            *db.engine.execute("SELECT * from users where vk_uid = {}".format(request.json['uid'])).fetchone()[4:]]
    else:
        output_TF = [
            *db.engine.execute("SELECT * from users where tg_uid = '{}'".format(request.json['uid'])).fetchone()[4:]]
    buffer = db.engine.execute("SELECT date, time, description FROM deadlines").fetchall()
    return json.dumps(list(map(list, get_schedule(output_TF, buffer, 'Overdue'))))


def get_schedule(output_TF: list, buffer: list, position: str) -> list:
    """
    Функция возвращает расписание для конкретного пользователя, в зависимости от его позиции
    output_TF - список отмеченных/неотмеченных дедлайнов
    buffer - список ВСЕХ дедлайнов
    position - позиция пользователя в меню бота(определяется тип расписания который нужно вернуть)
    return - возвращает список просроченных/текущих дедлайнов в зависимости от параметров
    """
    output = []
    for i in range(len(buffer)):
        if int(output_TF[i]) == 0 and \
                datetime.datetime(year=int(buffer[i][0][6:]), month=int(buffer[i][0][3:5]), day=int(buffer[i][0][:2]),
                                  hour=int(buffer[i][1][:2]), minute=int(buffer[i][1][4:])) >= datetime.datetime.now() \
                and position == 'Current':
            output.append(buffer[i])

        elif int(output_TF[i]) == 0 and \
                datetime.datetime(year=int(buffer[i][0][6:]), month=int(buffer[i][0][3:5]), day=int(buffer[i][0][:2]),
                                  hour=int(buffer[i][1][:2]), minute=int(buffer[i][1][4:])) < datetime.datetime.now() \
                and position == 'Overdue':
            output.append(buffer[i])
    return output


@app.route('/api', methods=['POST'])
def post_handler():
    """
    Функция-обработчик входящего POST запроса в зависимости от входящих параметров или добавляет пользователя в бд
    или добавляет дедлайн в БД.
    return - возвращает строку 'Done'
    """
    if request.args['type_of_action'] == 'add_user':
        return add_user(request.json)
    elif request.args['type_of_action'] == 'add_deadline':
        return add_deadline(request.json)


def add_user(params: dict) -> str:
    """
    В зависимости от uid_type в params добавляет пользователя по VK/TG UID
    params - словарь вида: {'uid_type': 'vk/tg', 'uid': '22832132'}. Нужен для идентификации клиента, пользователь
    VK/TG
    return - возвращает строку 'Done'
    """
    if params['uid_type'] == 'vk':
        db.session.add(users(vk_uid=params['uid'], user_position='Main'))
        db.session.commit()
        return 'Done'
    else:
        db.session.add(users(tg_uid=params['uid'], user_position='Main'))
        db.session.commit()
        return 'Done'

def add_deadline(params: dict) -> str:
    """
    Добавляет дедлайны в таблицу.
    params - словарь вида: {'date': '22.12.2021', 'time': "12:20", "description": "Math121"}
    return - возвращает строку 'Done'
    """
    db.session.add(deadlines(date=params['date'], time=params['time'],
                             description=params['description']))
    db.session.commit()
    table_num = db.engine.execute("SELECT MAX(id) FROM deadlines").fetchone()[0]
    db.engine.execute("ALTER TABLE users ADD COLUMN d{} VARCHAR DEFAULT False".format(table_num))
    return 'Done'


@app.route('/api', methods=['PUT'])
def put_handler():
    """
    Функция-обработчик входящего PUT запроса в зависимости от входящих параметров или меняет позицию пользователя
    в меню в базе данных или отмечает дедлайны выполненными
    return - возвращает строку 'Done'
    """
    if request.args['type_of_action'] == 'new_pos':
        return change_new_position(request.json)
    elif request.args['type_of_action'] == 'deadline_done':
        return mark_deadline_done(request.json)


def change_new_position(params: dict) -> str:
    """
    Меняет позицию пользователя в меню в базе данных.
    params - словарь вида:{'uid_type': 'vk/th', 'uid': '12345678', 'new_pos': 'Overdue/Current/Main'}
    return - возвращает строку 'Done'
    """
    if params['uid_type'] == 'vk':
        db.engine.execute("UPDATE users SET user_position='{}' WHERE vk_uid LIKE {}".format(params['new_pos'],
                                                                                        str(params['uid'])))
    else:
        db.engine.execute("UPDATE users SET user_position='{}' WHERE tg_uid LIKE {}".format(params['new_pos'],
                                                                                            str(params['uid'])))
    return "Done"


def mark_deadline_done(params: dict):
    """
    Отмечает дедлайн выполненным в базе данных.
    params - словарь вида: {'uid_type': 'vk/tg', 'uid': '12345678', 'what_del': ['Math']}
    return - возвращает строку 'Done'
    """
    if params['uid_type'] == 'vk':
        for descr in params['what_del']:
            table_id = db.engine.execute("SELECT id FROM deadlines WHERE description LIKE '{}'".format(descr)). \
                fetchall()[-1][0]
            db.engine.execute("UPDATE users SET d{}=1 WHERE vk_uid LIKE {}".format(str(table_id),
                                                                                   str(params['uid'])))
    else:
        for descr in params['what_del']:
            table_id = db.engine.execute("SELECT id FROM deadlines WHERE description LIKE '{}'".format(descr)). \
                fetchall()[-1][0]
            db.engine.execute("UPDATE users SET d{}=1 WHERE tg_uid LIKE {}".format(str(table_id),
                                                                                   str(params['uid'])))
    return 'Done'


if __name__ == '__main__':
    db.create_all()
    app.run()
