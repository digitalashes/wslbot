from asyncio import ensure_future
from re import search as re_search

from telethon.events import NewMessage

from config.logger import logger
from config.settings import CHAT_NAME
from config.settings import SECRET_STOP_WORD
from config.settings import SKIP_MESSAGES
from .utils import check_last_message


async def produce(queue, client, user):
    logger.info('Starting producer...')

    @client.on(NewMessage(from_users=CHAT_NAME, incoming=True))
    async def incoming_message_handler(event):

        message_obj = event.message
        message_text = message_obj.message

        if any(re_search(pattern, message_text) for pattern in SKIP_MESSAGES) or \
                message_obj.photo is not None:
            return
        else:
            await queue.put(message_obj)
            logger.info(f'Incoming message. {message_text[:150]}...')

    @client.on(NewMessage(chats=CHAT_NAME, outgoing=True))
    async def outgoing_message_handler(event):
        message_obj = event.message
        if SECRET_STOP_WORD in message_obj.message.lower():
            await client.disconnect()
            checker.cancel()

    checker = ensure_future(check_last_message(user))
    await client.run_until_disconnected()
