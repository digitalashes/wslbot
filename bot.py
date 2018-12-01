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


async def update(user, message):
    if '👥' in message:
        await user.update_info(message)
    elif '🍗' in message:
        await user.update_stats(message)
    elif 'ПРИПАСЫ В РЮКЗАКЕ' in message:
        await user.update_food(message)
    elif 'Уровень голода:' in message:
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

        if any(re.search(pattern, message) for pattern in settings.CAMP_MESSAGES):
            logger.info('Returned to Camp')
            await user.ping()
            queue.task_done()
            continue

        if user.is_hungry:
            await user.eat()
            queue.task_done()
            continue

        if any(re.search(pattern, message) for pattern in settings.COMBAT_MESSAGES) or \
                user.ACTIONS_MAPPING['attack'] in available_buttons:
            await user.attack()
            queue.task_done()
            continue

        if 'Уверен, что хочешь отправиться обратно?' in message:
            await user.confirm()
            queue.task_done()
            continue
        elif user.distance >= settings.MAX_DISTANCE:
            await user.go_home()
            queue.task_done()
            continue

        await user.go_ahead()
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
        if any(re.search(pattern, message_text) for pattern in settings.SKIP_MESSAGES) or \
                message_obj.photo is not None:
            return
        else:
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
                                  ).start(settings.PHONE_NUMBER)
    async with client:
        if not await client.is_user_authorized():
            await client.send_code_request(settings.PHONE_NUMBER)
            await client.sign_in(settings.PHONE_NUMBER, input('Enter code: '))

        entity = await client.get_entity(settings.CHAT_NAME)
        send_message = partial(client.send_message, entity)
        user = User(send_message, logger)
        queue = asyncio.Queue()
        logger.info('Preparing...')
        consumer = asyncio.ensure_future(consume(queue, user))
        await produce(queue, client, user)
        await queue.join()
        consumer.cancel()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    try:
        logger.info('Starting...')
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Finishing...')
