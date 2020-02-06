from itertools import chain
from re import search as re_search

from config.logger import logger
from config.settings import CAMP_MESSAGES
from config.settings import COMBAT_MESSAGES
from config.settings import MAX_DISTANCE
from .utils import update


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

        if any(re_search(pattern, message) for pattern in CAMP_MESSAGES):
            logger.info('Returned to Camp')
            await user.ping()
            queue.task_done()
            continue

        if user.is_hungry:
            await user.eat()
            queue.task_done()
            continue

        if any(re_search(pattern, message) for pattern in COMBAT_MESSAGES) or \
                user.ACTIONS_MAPPING['attack'] in available_buttons:
            await user.attack()
            queue.task_done()
            continue

        if 'Уверен, что хочешь отправиться обратно?' in message:
            await user.confirm()
            queue.task_done()
            continue

        elif user.distance >= MAX_DISTANCE:
            await user.go_home()
            queue.task_done()
            continue

        await user.go_ahead()
        queue.task_done()
