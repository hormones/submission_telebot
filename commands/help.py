from telethon import events
from telethon.tl.types import BotCommandScopePeer

import config
import db
import wrapper
from base.types import Chat
from config import client
from i18n import DEFAULT_LANG, i18n

from . import __common__


def _get_gelp_text(event, is_admin, args=None):
    '''
    if exists args, return command help detail
    else return command help`s text 
    '''
    # get command help detail if exists args
    if args and args in __common__.ALL_COMMANDS:
        command_info = __common__.ALL_COMMANDS[args]
        if 'help_detail' in command_info:
            return i18n(command_info['help_detail'])
        else:
            return i18n(command_info['desc'])

    # return command help without args
    help_text = ''
    if is_admin:
        help_text = i18n('$command_help_text_admin$') + "\n"
        # you will get error: " Message does`nt exist " when click the link in desktop client, just ignore it
        help_text += '\n' + i18n('$approve_channel_link$').format(config.APPROVE_CHANNEL.title, config.APPROVE_CHANNEL.id)
    else:
        help_text = i18n('$command_help_text$') + "\n"
    if config.SUBMISSION_CHANNEL.username:
        help_text += '\n' + i18n('$submission_channel_link$').format(config.SUBMISSION_CHANNEL.title, config.SUBMISSION_CHANNEL.username)
    # help_text += '\n' + i18n('$submission_group_link$').format(config.SUBMISSION_GROUP.title, config.SUBMISSION_GROUP.username)
    return help_text


async def init():
    '''
    command useage: /help [command_name]
    command useage: /start
    '''
    @client.on(events.NewMessage(pattern='/help( .*)?', incoming=True))
    @wrapper.event_wrapper('help')
    async def command_help_handler(event, is_admin):
        '''
        command useage: /help [command_name]
        '''
        args = (event.pattern_match.group(1) or '').strip()
        text = _get_gelp_text(event, is_admin, args)

        await event.respond(text)

    @client.on(events.NewMessage(pattern='/start( .*)?', incoming=True))
    @wrapper.event_wrapper('help') # special check by help command for /start
    async def command_start_handler(event, is_admin):
        '''
        command useage: /start
        '''
        # args = (event.pattern_match.group(1) or '').strip()

        # reset peer commands if admin or lang code is not default
        chat = db.chat_query(event.chat_id) or Chat(event.chat_id, 1, DEFAULT_LANG)
        if is_admin or chat.lang_code != DEFAULT_LANG:
            peer = await event.get_input_chat()
            await __common__.register_commands(is_admin, BotCommandScopePeer(peer), chat.lang_code)

        db.chat_insert_ignore(chat)
        await event.respond(_get_gelp_text(event, is_admin))
