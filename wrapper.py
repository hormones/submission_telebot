import asyncio
import functools
import logging
import commands

import config
import db
from i18n import DEFAULT_LANG, i18n


async def _event_prehandler(event, command=None):
    '''
    1. check chat is banned or not
    1. set asyncio task event params
    2. check request chat is valid
    '''
    lang_code = DEFAULT_LANG
    chat = db.chat_query(event.chat_id)
    if chat:
        if not chat.status:
            await event.respond(i18n('$user_banned$'))
            return False, False
        lang_code = chat.lang_code or DEFAULT_LANG

    # 1. set asyncio task event params
    task = asyncio.current_task()
    task.chat_id = event.chat_id
    task.lang_code = lang_code
    logging.debug(f"set param for task: chat_id = {event.chat_id}, lang_code = {lang_code}")
    # 2. check request chat is valid
    is_admin = event.chat_id in config.SUPER_ADMINS
    if command:
        if command is 'reply':
            return True, False
    else:
        return True, is_admin

    if (is_admin and command not in commands.ALL_COMMANDS) or (not is_admin and command not in config.USER_COMMAND_KEYS):
        await event.respond(i18n('$unknown_command$'))
        return False, is_admin

    return True, is_admin


async def _event_posthandler(event, command=None):
    pass


def event_wrapper(command=None):
    def decorator(handler):
        @functools.wraps(handler)
        async def wrapper(event, **kwargs):
            allowed, is_admin = await _event_prehandler(event, command)
            if not allowed:
                logging.warning(f"event_wrapper: event is not allowed, event: {event.chat_id}, command: {command}")
                return
            result = await handler(event, is_admin)
            await _event_posthandler(event, command)
            return result
        return wrapper
    return decorator
