import requests
import datetime
import json
import vk_api
from vk_api.utils import get_random_id
vk = vk_api.VkApi(
        token='3bf2b5ede024bad5fff48b06904b877a50229c6fa7520d260054bcd421957e0527f3531a60bb1105f6889').get_api()

def mainLoop():
    """
    Функция отправки уведомлений пользователю VK. Постоянно проверяет время и если необходимо отправляет уведомления
    """
    prev_hour = -1
    while True:
        if datetime.datetime.now().time().hour > prev_hour:
            vk_users = json.loads(requests.get('http://127.0.0.1:5000/api/get_users',
                                                json={'uid_type': 'vk'}).text)
            for i in vk_users:
                deadlines = json.loads(requests.get('http://127.0.0.1:5000/api/Current',
                                            json={'uid_type': 'vk', 'uid': i}).text)
                time_now = datetime.datetime.now().time()
                for deadline in deadlines:
                    if (time_now.hour == int(deadline[1][0:2]) and
                            (datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                    day=int(deadline[0][:2])) == datetime.datetime.now().date() or
                            datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                    day=int(deadline[0][:2])) == (datetime.datetime.now() + datetime.timedelta(days=1)).date() or
                            datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                    day=int(deadline[0][:2])) == (datetime.datetime.now() + datetime.timedelta(days=3)).date() or
                            datetime.date(year=int(deadline[0][6:]), month=int(deadline[0][3:5]),
                                    day=int(deadline[0][:2])) == (datetime.datetime.now() + datetime.timedelta(days=7)).date()
                        )):
                        vk.messages.send(peer_id=int(i), random_id=get_random_id(),
                                         message='Скоро заканчивается дедлайн: {} {} {}'.format(deadline[2],
                                                                                                deadline[0],
                                                                                                deadline[1]))
            prev_hour = datetime.datetime.now().time().hour




if __name__ == '__main__':
    mainLoop()
