import asyncio
from functools import partial

import uvloop
from telethon import TelegramClient

from bot import consume
from bot import produce
from config import logger
from config.settings import API_HASH
from config.settings import API_ID
from config.settings import CHAT_NAME
from config.settings import PHONE_NUMBER
from config.settings import SESSION_NAME
from models import User


async def main():
    client = await TelegramClient(
        SESSION_NAME,
        API_ID,
        API_HASH,
    ).start(PHONE_NUMBER)

    async with client:
        if not await client.is_user_authorized():
            await client.send_code_request(PHONE_NUMBER)
            await client.sign_in(PHONE_NUMBER, input('Enter code: '))

        entity = await client.get_entity(CHAT_NAME)
        send_message = partial(client.send_message, entity)

        user = User(send_message, logger)
        queue = asyncio.Queue()

        logger.info('Preparing...')

        consumer = asyncio.ensure_future(consume(queue, user))
        await produce(queue, client, user)
        await queue.join()
        consumer.cancel()


if __name__ == '__main__':
    uvloop.install()

    try:
        logger.info('Starting...')
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Finishing...')
