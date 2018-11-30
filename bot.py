import asyncio
import datetime
import re
from functools import partial
from itertools import chain

import uvloop
from telethon import TelegramClient, events

from config import settings
from config.logger import logger
from models.users import User

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def update(user, message):
    if '👥' in message:
        logger.info(f'Update info')
        await user.update_info(message)
    elif '🍗' in message:
        logger.info(f'Update stats')
        await user.update_stats(message)
    elif 'ПРИПАСЫ В РЮКЗАКЕ' in message:
        logger.info('Update food')
        await user.update_food(message)
    elif 'Уровень голода:' in message:
        logger.info(f'Update hungry level')
        await user.update_hungry_level(message)
    logger.info(repr(user))


async def consume(queue, user):
    logger.info('Starting consumer...')
    while True:
        message_obj = await queue.get()
        message = message_obj.message
        user.last_message = message_obj.date
        try:
            available_buttons = [btn.text for btn in chain(*message_obj.buttons)]
        except TypeError:
            logger.error('Available buttons not found')
            available_buttons = []
        await update(user, message)
        if 'Главарь:' in message:
            logger.info('Returned to Camp')
            await user.ping()
            queue.task_done()
            continue
        if user.is_hungry:
            logger.warning(f'User is hungry. Hungry level - {user.hunger}')
            await user.eat(logger)
            queue.task_done()
            continue
        if any(re.search(pattern, message) for pattern in settings.COMBAT_MESSAGES) or \
                user.ACTIONS_MAPPING['attack'] in available_buttons:
            logger.info('Attacking')
            await user.attack()
            queue.task_done()
            continue
        if 'Уверен, что хочешь отправиться обратно?' in message:
            await user.confirm()
            queue.task_done()
            continue
        elif user.distance >= settings.MAX_DISTANCE:
            logger.warning('You are close to maximum distances. Return back.')
            await user.go_home()
            queue.task_done()
            continue

        await user.go_ahead()
        logger.info('Moving on')
        queue.task_done()


async def check_last_message(user):
    def __check_time(_datetime, **_timedelta):
        now = datetime.datetime.utcnow().replace(tzinfo=_datetime.tzinfo)
        return _datetime < now - datetime.timedelta(**_timedelta)

    while True:
        if __check_time(user.last_message, minutes=3):
            logger.warning(f'check_last_message sent pip_boy command')
            await user.ping()
        await asyncio.sleep(60)


async def produce(queue, client, user):
    logger.info('Starting producer...')

    @client.on(events.NewMessage(from_users=settings.CHAT_NAME, incoming=True))
    async def incoming_message_handler(event):
        message_obj = event.message
        message_text = message_obj.message
        if any(re.search(pattern, message_text) for pattern in settings.SKIP_MESSAGES):
            return
        await queue.put(message_obj)
        logger.info(f'Incoming message. {message_text[:150]}...')

    @client.on(events.NewMessage(chats=settings.CHAT_NAME, outgoing=True))
    async def outgoing_message_handler(event):
        message_obj = event.message
        if settings.SECRET_STOP_WORD in message_obj.message.lower():
            await client.disconnect()
            checker.cancel()

    checker = asyncio.ensure_future(check_last_message(user))
    await client.run_until_disconnected()


async def main():
    client = await TelegramClient(settings.SESSION_NAME,
                                  settings.API_ID,
                                  settings.API_HASH,
                                  loop=asyncio.get_event_loop()
                                  ).start(settings.PHONE_NUMBER)
    async with client:
        if not await client.is_user_authorized():
            await client.send_code_request(settings.PHONE_NUMBER)
            await client.sign_in(settings.PHONE_NUMBER, input('Enter code: '))

        entity = await client.get_entity(settings.CHAT_NAME)
        send_message = partial(client.send_message, entity)
        user = User(send_message)
        queue = asyncio.Queue()
        logger.info('Preparing...')
        consumer = asyncio.ensure_future(consume(queue, user))
        await produce(queue, client, user)
        await queue.join()
        consumer.cancel()


if __name__ == '__main__':
    try:
        logger.info('Starting...')
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Finishing...')
