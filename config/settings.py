from environs import Env

env = Env()
env.read_env()

DEBUG = env.bool('DEBUG')
API_ID = env.str('API_ID')
API_HASH = env.str('API_HASH')
SESSION_NAME = env.str('SESSION_NAME')
PHONE_NUMBER = env.str('PHONE_NUMBER')
CHAT_NAME = env.str('CHAT_NAME')
MAX_DISTANCE = env.int('MAX_DISTANCE')
HUNGER_LEVEL = env.int('HUNGER_LEVEL')
SKIP_FOOD = [bytes(e, 'utf-8').decode('unicode_escape') for e in env.list('SKIP_FOOD', subcast=str)]
SECRET_STOP_WORD = env.str('SECRET_STOP_WORD', '').lower()
assert SECRET_STOP_WORD, 'Secret stop word must be present'

SKIP_MESSAGES = [
    'Тебя ждут более сильные враги и опасные ситуации.',
    'Выносливость восстановлена.',
    'Новости Wasteland Wars',
    'Чем дальше ты заходишь в Пустоши - тем сложнее тебе будет там выжить',
    'Это что, поза боевого ягненка?',
    'Ты отправился в лагерь.',
    'Трезво оценив свои силы, ты достал оружие и приготовился к бою.',
    'Что-то пошло не так.',
    'Твое местоположение:',
    'Ты решил вступить в схватку с противником.',
    'Бросая вызов Пустоши, ты отправился в самые ее недра.',
    'Ты водрузил оружие на плечо и пошел по пустынной дороге.',
    'Удачи тебе в бою',
]
COMBAT_MESSAGES = [
    'Ты не сможешь увильнуть от противника.',
    'Во время вылазки на тебя напал',
    'Решай, что будешь делать.',
    'Тебе не уйти от противника',
    'Удачи в бою, странник.',
]
