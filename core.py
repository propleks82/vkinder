from datetime import datetime

import vk_api
from vk_api.exceptions import ApiError

from config import access_token


class VkTools():
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)

    def _bdate_to_age_(self, bdate):
        if bdate is not None:
            bdate_year = bdate.split('.')[-1]
            curent_year = datetime.now().year
            age = curent_year - int(bdate_year) 
        else: 
            age = None
        return age

    def get_profile_info(self, user_id):
        try:
            info, = self.vkapi.method('users.get',
                {'user_id': user_id,
                'fields': 'city, sex,relation,bdate'
                }
                )
        except ApiError as e:
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if
            'first_name' in info and 'last_name' in info else None,
            'age': self._bdate_to_age_(info.get('bdate')), 
            'sex': info.get('sex'),
            'city': info.get('city')['title'] if info.get('city') is not None else None,
            'relation': info.get('relation') 
            }
        return result

    def get_city(self, city):
        try:
            cities = self.vkapi.method('database.getCities',
                {'q': city, 'count': 1}
                )
            if len(cities['items']) > 0:
                return cities['items'][0]
        except ApiError as e:
            print(f'error = {e}')

    def users_search(self, params, offset:int=0):
        try:
            users = self.vkapi.method('users.search',
                {'count': 30,
                'offset': offset,
                'hometown': params['city'],
                'sex': 1 if params['sex'] == 2 else 2,
                'has_photo': True,
                'age_from': params['age'] - 3,
                'age_to': params['age'] + 3,
                'relation': 6,
                'is_closed': False})
        except ApiError as e:
            users = []
            print(f'error = {e}')

        res = [{'name': user['first_name'] + ' ' + user['last_name'],
            'id': user['id']} for user in users['items'] if user['is_closed'] is False]

        return res


    def get_photos(self, owner_id):
        try:
            photos = self.vkapi.method('photos.get',
                {'owner_id': owner_id,
                'album_id': 'profile',
                'extended': 1
                }
                )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        res = [{'owner_id': photo['owner_id'],
            'photo_id': photo['id'],
            'likes': photo['likes']['count'],
            'comments': photo['comments']['count']
            } for photo in photos['items'] 
            ]
        res.sort(key= lambda d: d['likes'] + d['comments'], reverse=True)
        return res[:3]    
