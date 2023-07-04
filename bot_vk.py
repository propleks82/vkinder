import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from config import access_token, comunity_token
from core import VkTools
from database import Base, add_user, check_user, engine


class VkBot():
    def __init__(self, comunity_token, access_token, engine):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vkapi = VkTools(access_token)
        self.engine = engine
        self.params = None
        self.finded_users = None
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        '''Функция отправки сообщений пользователю'''
        self.vk.method('messages.send',
            {'user_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': get_random_id()}
            )


    def event_handler(self):
        '''Обработчик событий'''
        guide = f'Для взаимодействия с поисковым ботом используйте следующие команды без кавычек:\n "привет" - для начала работы;\n "искать" - для  поиска пары;\n "пока" - для теплого прощания с ботом))) '

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if self.params is None:
                    self.params = self.vkapi.get_profile_info(event.user_id)
                if event.text.lower() == 'привет':
                    self.message_send(event.user_id, f'{self.params.get("name")}, тебя приветствую я !\n{guide}')
                elif event.text.lower() == 'искать':
                    if self.params.get("age") is None:
                        self.message_send(event.user_id,f"Пожалуйста, укажите ваш возраст, для этого введите команду 'возраст' и число через пробел.\nНапример: возраст 18")
                        continue
                    if self.params.get("city") is None:
                        self.message_send(event.user_id,f"Пожалуйста, укажите ваш город, для этого введите команду 'город' и название города через пробел.\nНапример: город Сыктывкар")
                        continue


                    self.message_send(                        event.user_id, 'Да начнется поиск!...')
                    print(self.params           )
                    if self.finded_users is None:
                        self.finded_users = self.vkapi.users_search(self.params, self.offset)


                    finded_user= None
                    new_find = []
                    for finded_user in self.finded_users:
                        if check_user(self.engine, event.user_id, finded_user['id']) != True:
                            new_find.append(finded_user)
                            print(new_find)
                    self.finded_users = new_find.copy()
                    print(self.finded_users)
                    finded_user= self.finded_users.pop(0)

                    photos = self.vkapi.get_photos(finded_user['id'])
                    photo_string = ''
                    for photo in photos:
                        photo_string += f'photo{photo["owner_id"]}_{photo["photo_id"]},'
                    self.offset += 3

                    self.message_send(
                        event.user_id, f'имя: {finded_user["name"]}\nСсылка: vk.com/id{finded_user["id"]}', attachment=photo_string)   
                    add_user(self.engine, event.user_id, finded_user['id'])

                elif event.text.lower().startswith("возраст"):
                    age = event.text.lower().split()[-1]
                    print(age)

                    try:
                        age = int(age)
                        print(age)
                    except ValueError:
                        self.message_send(event.user_id, 'Необходимо ввести число')
                        continue
                    self.params['age'] = age
                    self.message_send(event.user_id, 'Отлично!Зачет!')

                elif event.text.lower().startswith("город "):
                    city_input = ' '.join(event.text.lower().split()[1:])
                    city = self.vkapi.get_city(city_input)
                    if city is None:
                        self.message_send(event.user_id, 'Не нашел я такого города.... Давайте поищем другой.')
                    else:
                        self.params['city'] = city['title']
                        print(self.params)
                        self.message_send(event.user_id, f'Хм...Вы живете в г.{city["title"]}. Заносила нелегкая в эти места))) ')


                elif event.text.lower() == 'пока':
                    self.message_send(event.user_id, f"До новых встреч!\nОбнял....заплакал....")

                else:
                    self.message_send(event.user_id, 'Что-то пошло не так... {guide}')
                    continue


if __name__ == '__main__':
    bot = VkBot(comunity_token, access_token, engine=engine)
    bot.event_handler()
    
