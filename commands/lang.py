import logging
import re

from telethon import Button, events
from telethon.tl.types import BotCommandScopePeer

import config
import db
import wrapper
from base import util
from base.types import Chat
from config import client
from i18n import DEFAULT_LANG, LANGS, i18n

from . import __common__

__buttons = []


async def init():
    global __buttons
    for lang_code, lang_desc in LANGS.items():
        __buttons.append(Button.inline(lang_desc, f'lang:{lang_code}'))

    @client.on(events.NewMessage(pattern='/lang( .*)?', incoming=True))
    @wrapper.event_wrapper('lang')
    async def command_lang_handler(event, is_admin):
        '''
        command useage: /lang
        '''
        # args = (event.pattern_match.group(1) or '').strip()
        await event.respond(message=i18n('$command_lang_desc$'), buttons=__buttons)

    @client.on(events.CallbackQuery(data=re.compile(b'lang:')))
    @wrapper.event_wrapper()
    async def command_lang_handler_callback_query(event: events.CallbackQuery.Event, is_admin):
        action, lang_code = event.data.decode().split(':')
        logging.debug(f"change lang --> chat_id: {event.chat_id} lang_code: {lang_code}")

        peer = await event.get_input_chat()
        is_admin = event.chat_id in config.SUPER_ADMINS
        await __common__.register_commands(is_admin, BotCommandScopePeer(peer), lang_code)
        db.chat_update(Chat(chat_id=event.chat_id, lang_code=lang_code))
        await event.respond(i18n('$setting_success$', lang_code))
