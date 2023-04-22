from telethon import events
from base import util

import config
from config import client
from i18n import i18n

from . import __common__


async def init():
    '''
    command useage: /feedback feedback_text
    '''
    @client.on(events.NewMessage(pattern='/feedback( .*)?', incoming=True))
    async def command_feedback_handler(event):
        '''
        command useage: /feedback feedback_text
        '''
        util.set_asyncio_params(event)
        allowed, is_admin = await __common__.chat_check(event, 'feedback')
        if not allowed or is_admin:
            return
        args = (event.pattern_match.group(1) or '').strip()
        if not args:
            await event.respond(i18n('$command_feedback_null_error$'))
            return
        
        # send feedback to approve channel
        feed_back = args + i18n('$command_feedback_suffix$').format(event.sender.first_name, event.sender_id)
        await client.send_message(config.APPROVE_CHANNEL, feed_back)

        # after sending, respond to user
        await event.respond(i18n('$command_feedback_text$'))
