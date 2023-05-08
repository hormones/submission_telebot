import asyncio
import logging

from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.types import (BotCommand, BotCommandScopeDefault,
                               BotCommandScopePeer)

import config
import db
from base.types import Chat
from config import client
from i18n import DEFAULT_LANG, LANGS, i18n


async def _register_chat_commands():
    '''
    register commands for existing chats if admin or user`s lang_code is not default
    '''
    chats = db.chat_query_all()
    for chat in chats:
        admin = chat.chat_id in config.SUPER_ADMINS
        if admin or chat.lang_code != DEFAULT_LANG:
            try:
                peer = await client.get_input_entity(chat.chat_id)
                await register_commands(admin, BotCommandScopePeer(peer), chat.lang_code)
            except Exception as e:
                config.DEBUG and logging.exception(str(e))
                pass


async def _register_reply_commands():
    if config.APPROVE_GROUP:
        reply_commands = I18N_REPLY_COMMANDS[DEFAULT_LANG]
        peer = await client.get_input_entity(config.APPROVE_GROUP)
        await client(SetBotCommandsRequest(commands=reply_commands, scope=BotCommandScopePeer(peer), lang_code=''))


def _get_bot_commands(command_keys, admin=False):
    i18n_commands = {}

    for lang_code in LANGS:
        lang_commands = []
        for key in command_keys:
            if key not in ALL_COMMANDS:
                raise ValueError(f'unknown command: {key}')
            desc = ALL_COMMANDS[key]['desc']
            if admin:
                desc = ALL_COMMANDS[key].get('admin_desc', desc)
            lang_commands.append(BotCommand(key, i18n(desc, lang_code)))
        i18n_commands[lang_code] = lang_commands
    return i18n_commands


async def register_commands(admin, scope, lang_code):
    i18n_commands = I18N_ADMIN_COMMANDS[lang_code] if admin else I18N_USER_COMMANDS[lang_code]
    # await client(ResetBotCommandsRequest(scope=scope, lang_code=''))
    # SetBotCommandsRequest`slang_code  can be '' instead of None, it`s Telethon`s bug
    await client(SetBotCommandsRequest(commands=i18n_commands, scope=scope, lang_code=''))


async def init():
    '''
    init chat commands for admin and user
    '''
    global I18N_ADMIN_COMMANDS, I18N_USER_COMMANDS, I18N_REPLY_COMMANDS

    for super_admin in config.SUPER_ADMINS:
        db.chat_insert_ignore(Chat(super_admin, 1, DEFAULT_LANG))

    # cache commands by lang_code
    admin_keys = list(ALL_COMMANDS.keys())
    admin_keys.remove('reply')
    admin_keys.remove('feedback')
    I18N_ADMIN_COMMANDS = _get_bot_commands(admin_keys, True)
    I18N_USER_COMMANDS = _get_bot_commands(config.USER_COMMAND_KEYS, False)
    I18N_REPLY_COMMANDS = _get_bot_commands(['reply'], False)

    # for lang_code in LANGS.keys():
    #     await client(ResetBotCommandsRequest(BotCommandScopeDefault(), ''))
    logging.info(f'set bot commands for default: {DEFAULT_LANG}')
    # register user`s default commands by lang_code
    await register_commands(False, BotCommandScopeDefault(), DEFAULT_LANG)
    await _register_reply_commands()
    # oh my god, if you register the chats commands too fast,
    # it will not work sometimes because you just registered default commands
    await asyncio.sleep(2)
    # register admin`s commands and chat`s commands by lang_code
    await _register_chat_commands()


# there are all the commands that you can use
ALL_COMMANDS = {
    "help": {
        "desc": "$command_help_desc$",
    },
    "ban": {
        "desc": "$command_ban_desc$",
        "help_detail": "$command_ban_help_detail$"
    },
    "lang": {
        "desc": "$command_lang_desc$",
    },
    "setting": {
        "desc": "$command_setting_desc$",
    },
    "feedback": {
        "desc": "$command_feedback_desc$",
    },
    "reply": {
        "desc": "$command_reply_desc$",
    },
}
# I18N_ADMIN_COMMANDS/I18N_USER_COMMANDS/I18N_REPLY_COMMANDS, commands cached by lang_code ---> {lang_code: [BotCommand]}
I18N_ADMIN_COMMANDS = None
I18N_USER_COMMANDS = None
I18N_REPLY_COMMANDS = None
