# Wasteland Wars Bot
Этот проект содержит исходники для бота который автоматически бегает по пустоши и бьёт мобов.

> [!WARNING]
> За использование данного бота, ваш игровой аккаунт может быть забанен.

### Установка проекта
1. Убедитесь что у вас установлен Python версии 3.7 или выше
1. Убедитесь что у вас установлен Pipenv
1. Склонируйте этот репозиторий
1. Установите пакеты командой `pipenv install`

### Запуск проекта
1. Скопируйте `.env.example` файл в папку `config` и переименнуйте его в `.env`
1. Так как бот использует библиотеку [Telethon](https://github.com/LonamiWebs/Telethon) то загляните в её документацию,
 что бы понять, откуда получить значения `API_ID` и `API_HASH`
1. Заполните константы значениями, где
```
DEBUG - python debug
PYTHONASYNCIODEBUG - python async debug
API_ID - https://github.com/LonamiWebs/Telethon#creating-a-client
API_HASH - https://github.com/LonamiWebs/Telethon#creating-a-client 
SESSION_NAME - название сессии
PHONE_NUMBER - номер телефона
CHAT_NAME=Wasteland Wars (название чата игры)
MAX_DISTANCE - до какого километра ходим
HUNGER_LEVEL - при каком пороге голода начинаем есть еду
SKIP_FOOD=Конфета,Яблоко (что не едим)
SECRET_STOP_WORD=haha (при отправке этого слова в чат, бот останавливается)
```
