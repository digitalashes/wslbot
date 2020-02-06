from asyncio import sleep as asyncio_sleep
from datetime import datetime
from datetime import timedelta

from config.logger import logger


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


async def check_last_message(user):
    def __check_time(_datetime, **_timedelta):
        now = datetime.utcnow().replace(tzinfo=_datetime.tzinfo)
        return _datetime < now - timedelta(**_timedelta)

    while True:
        if __check_time(user.last_message, minutes=3):
            logger.warning(f'check_last_message sent pip_boy command')
            await user.ping()
        await asyncio_sleep(60)
