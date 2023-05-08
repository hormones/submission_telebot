import logging
import re

from telethon import Button, events

import config
import wrapper
from base import util
from config import client
from i18n import i18n

from . import __common__


def _setting_handler(event):
    debug_status = i18n(('$enabled$' if config.DEBUG else '$disabled$'))
    debug_button = i18n(('$disable_debug_mode$' if config.DEBUG else '$enable_debug_mode$'))

    approve_status = i18n(('$enabled$' if config.APPROVE else '$disabled$'))
    approve_button = i18n(('$disable_approve_mode$' if config.APPROVE else '$enable_approve_mode$'))

    text = i18n('$command_setting_text$').format(debug_status, approve_status)
    buttons = [
        [
            Button.inline(debug_button, f"setting:debug:{config.DEBUG}"),
            Button.inline(approve_button, f"setting:approve:{config.APPROVE}")
        ]
    ]
    return text, buttons


async def init():
    @client.on(events.NewMessage(pattern='/setting( .*)?', incoming=True))
    @wrapper.event_wrapper('setting')
    async def command_setting_handler(event, is_admin):
        '''
        command useage: /setting
        you can use this command to change the bot's default settings
        '''
        # args = (event.pattern_match.group(1) or '').strip()
        text, buttons = _setting_handler(event)
        await event.respond(text, buttons=buttons)

    @client.on(events.CallbackQuery(data=re.compile(b'setting:')))
    @wrapper.event_wrapper()
    async def setting_handler_callback_query(event: events.CallbackQuery.Event, is_admin):
        action, key, data = event.data.decode().split(':')
        if key == 'debug':
            config.DEBUG = not util.parse_bool(data)
            config.LOGGING.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
            config.LOGGING_FILE.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
        elif key == 'approve':
            config.APPROVE = not util.parse_bool(data)
        else:
            return
        text, buttons = _setting_handler(event)
        await event.edit(text, buttons=buttons)
