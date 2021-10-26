import requests
from random import randrange
import json
from Files.Files import *
from pprint import pprint
import time


class VK:

    def __init__(self):
        list_hello = ['привет', 'Привет', 'хай', 'Хай', 'здорово', 'Здорово']
        list_bye_bye = ['пока', 'Пока', 'Bye', 'bye', 'bye bye']
        list_search = ['Поиск', 'поиск', 'Найти', 'найти', 'Найди', 'найди', 'п']
        self.get_data_session()
        while True:
            data = self.get_messages()
            if data:
                message = data['message']
                user_id = data['from_user_id']
                user_params = self.get_user_params(user_id)
                # print(user_params)
                if message in list_hello:
                    self.send_message(f"Привет, {user_params['response'][0]['first_name']}", user_id)
                    self.send_message('Напишите слово - Найти, и чат-бот VKinder найдёт для вас друзей)))', user_id)
                elif message in list_bye_bye:
                    self.send_message(f"До скорого... {user_params['response'][0]['first_name']}", user_id)
                elif message in list_search:
                    params_for_search = self.check_users_params(user_params)
                    search = self.get_users_search(params_for_search)
                    self.send_message('Начинаю поиск...секундочку, пожалуйста...', user_id)
                    self.get_photos(self.get_list_users_id(search), user_id)

                else:
                    self.send_message('Не понимаю вашего запроса.', user_id)

    def get_list_users_id(self, search):
        list_id = []
        for dic in search['response']['items']:
            if not dic['is_closed']:
                list_id.append(dic['id'])
        return list_id

    def get_photos(self, list_id, user_id):
        url = 'https://api.vk.com/method/photos.get?'
        for search_id in list_id:
            params = {
                'owner_id': search_id,
                'album_id': 'profile',
                'extended': 1,
                'count': 10,
                'access_token': file.get_token()['vk_token'],
                'v': '5.131'
            }
            time.sleep(0.4)
            req = requests.get(url, params=params).json()
            # pprint(req)
            self.get_sort_photos(req, search_id, user_id)

    def get_sort_photos(self, my_dict, search_id, user_id):
        list_to_sort = []
        for l in my_dict['response']['items']:
            likes_comments = int(l['comments']['count']) + int(l['likes']['count'])
            list_to_sort.append((likes_comments, l['id']))
        data = sorted(list_to_sort, key=lambda x: x[0], reverse=True)[0:3]
        data_d = []
        for i in data:
            data_d.append('photo'+str(search_id)+'_'+str(i[1]))
        attachment = ','.join(data_d)
        self.send_photos_link(user_id, attachment, search_id)

    def send_photos_link(self, user_id, attachment, search_id):
        url = 'https://api.vk.com/method/messages.send?'
        params = {
            'user_id': user_id,
            "message": self.get_link_user(search_id),
            "attachment": attachment,
            'random_id': randrange(10 ** 7),
            'access_token': file.get_token()['vk_token_chat'],
            'v': '5.131'
        }
        req = requests.post(url, params=params).json()
        print(req)

    def get_link_user(self, search_id):
        link_user = 'https://vk.com/id' + str(search_id)
        return link_user

    def send_message(self, message, user_id):
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7),
            'access_token': file.get_token()['vk_token_chat'],
            'v': '5.81',
        }
        url = 'https://api.vk.com/method/messages.send?'
        request = requests.get(url, params=params)

    def get_users_search(self, params_for_search):
        url = 'https://api.vk.com/method/users.search?'
        req_search = requests.get(url, params=params_for_search).json()
        return req_search

    def get_data_session(self):
        vk_token_chat = file.get_token()['vk_token_chat']
        url_get_key = 'https://api.vk.com/method/groups.getLongPollServer?'
        vk_params = {
            'access_token': vk_token_chat,
            'v': '5.131',
            'group_id': 207822613
        }
        response = requests.get(url_get_key, params=vk_params).json()
        data = {'server': response['response']['server'],
                'key': response['response']['key'],
                'ts': response['response']['ts']}
        file.write_file_json('Files/data_session.json', data)
        return data

    def get_messages(self):
        url_server = file.read_file_json('Files/data_session.json')['server']
        params = {
            'act': 'a_check',
            'key': file.read_file_json('Files/data_session.json')['key'],
            'ts': file.read_file_json('Files/data_session.json')['ts'],
            'wait': '25',
            'v': '5.131',
        }
        req = requests.get(url_server, params=params).json()
        if req['updates']:
            data = file.read_file_json('Files/data_session.json')
            data['ts'] = req['ts']
            file.write_file_json('Files/data_session.json', data)
            return {'message': req['updates'][0]['object']['message']['text'],
                    'from_user_id': req['updates'][0]['object']['message']['from_id']}

    def get_user_params(self, user_id):
        url = 'https://api.vk.com/method/users.get?'
        params = {
            'access_token': file.get_token()['vk_token'],
            'v': '5.131',
            'user_id': user_id,
            'fields': 'city, sex, relation, bdate',
            'has_photo': 1,
        }
        user_params = requests.get(url, params=params).json()
        return user_params

    def check_users_params(self, user_params):
        params_for_search = {}
        key_list = user_params['response'][0].keys()
        my_list = user_params['response'][0]['bdate'].split('.')
        list_status = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        list_age = [x for x in range(10, 100)]

        if 'bdate' in key_list and user_params['response'][0]['bdate'] and len(my_list) == 3:
            params_for_search['age_from'] = user_params['response'][0]['bdate']
            params_for_search['age_to'] = user_params['response'][0]['bdate']
        else:
            while True:
                self.send_message('Введите ваш возраст(10 - 99 лет), пожалуйста: ', user_params['response'][0]['id'])
                age = int(self.get_messages()['message'])
                if age and age in list_age:
                    params_for_search['age_from'] = age
                    params_for_search['age_to'] = age
                    break

        if 'sex' in key_list and user_params['response'][0]['sex'] and user_params['response'][0]['sex'] != 0:
            params_for_search['sex'] = user_params['response'][0]['sex']
        else:
            self.send_message('Введите ваш пол, пожалуйста \n 1- женский \n 2 - мужской: ',
                              user_params['response'][0]['id'])
            sex = self.get_messages()['message']
            if sex:
                params_for_search['sex'] = sex

        if 'city' in key_list and user_params['response'][0]['city']['title']:
            params_for_search['hometown'] = user_params['response'][0]['city']['title']
        else:
            self.send_message('Введите ваш город, пожалуйста: ', user_params['response'][0]['id'])
            city = self.get_messages()['message']
            if city:
                params_for_search['hometown'] = city

        if 'relation' in key_list and user_params['response'][0]['relation']:
            params_for_search['status'] = user_params['response'][0]['relation']
        else:
            self.send_message("""Введите ваше семейное положение, пожалуйста\nВозможные значения:
                                1 — не женат/не замужем;
                                2 — есть друг/есть подруга;
                                3 — помолвлен/помолвлена;
                                4 — женат/замужем;з
                                5 — всё сложно;
                                6 — в активном поиске;
                                7 — влюблён/влюблена;
                                8 — в гражданском браке;
                                0 — не указано.
                                : """, user_params['response'][0]['id'])
            relation = int(self.get_messages()['message'])
            if relation and relation in list_status:
                params_for_search['status'] = relation

        params_for_search['access_token'] = file.get_token()['vk_token']
        params_for_search['v'] = '5.131'
        params_for_search['count'] = '30'
        print(params_for_search)
        return params_for_search


vk = VK()
