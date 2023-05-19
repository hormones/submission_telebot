import logging
import re
from math import ceil

from telethon import Button, events
from telethon.tl import types

import config
import db
import wrapper
from base.types import Chat
from config import client
from i18n import DEFAULT_LANG, i18n

from . import __common__


async def _user_handler(event, args):
    text = i18n('$unknown_error$')
    buttons = None

    try:
        args = int(args)
    except:
        pass

    try:
        entity = await client.get_entity(args)
        if entity.id and entity.id in config.SUPER_ADMINS:
            text = i18n('$super_admin_operate_error$')
        elif isinstance(entity, types.User):
            chat = db.chat_query(entity.id) or Chat(entity.id, 1, DEFAULT_LANG)
            text, buttons = _get_chat_status(event, entity, chat)
        else:
            text = i18n('$command_ban_user_setting_error$')
    except Exception as e:
        text = i18n('$invalid_opration$')
        logging.exception("ban command execute error, cannot handle user with id: %s\n%s",args, e)
    return text, buttons


def _get_chat_status(event, entity, chat: Chat):
    buttons = []
    ban_status, ban_desc, ban_btn_text = (0, '$normal$', '$ban$') if chat.status else (1, '$banned$', '$unban$')
    text = i18n('$command_ban_user_status$', event).format(entity.first_name, entity.id, i18n(ban_desc))
    buttons.append(Button.inline(i18n(ban_btn_text), f"ban_user:{ban_status}:{chat.chat_id}"))
    return text, buttons


async def _banned_page_handler(event, page_number=1, page_size=1):
    total, chats = db.chats_banned(page_number, page_size)
    if not total:
        return i18n('$command_ban_banned_zero_text$'), None
    if not chats and page_number != 1:
        return await _banned_page_handler(event, page_number-1)
    if not chats:
        return i18n('$no_more_data$'), None

    # build buttons, 2 buttons per row
    buttons = []
    chats_groups = [chats[i:i+2] for i in range(0, len(chats), 2)]
    for group in chats_groups:
        button_row = []
        for chat in group:
            entity = await client.get_entity(chat.chat_id)
            button_row.append(Button.inline(entity.first_name, f"banned:{page_number}:{chat.chat_id}"))
        buttons.append(button_row)

    # build page buttons
    page_buttons = []
    if page_number > 1:
        page_buttons.append(Button.inline(i18n('$previous_page$'), f"banned_page:{page_number-1}"))
    if total > page_number * page_size:
        page_buttons.append(Button.inline(i18n('$next_page$'), f"banned_page:{page_number+1}"))
    if page_buttons:
        buttons.append(page_buttons)

    text = i18n('$command_ban_banned_text$').format(total, page_number, ceil(total / page_size))
    return text, buttons


async def init():
    @client.on(events.NewMessage(pattern='/ban( .*)?', incoming=True))
    @wrapper.event_wrapper('ban')
    async def command_ban_handler(event, is_admin):
        '''
        command useage: /ban [user_id|username|@username]
        for detailed usage, please enter command in bot: /help ban
        '''
        # args can be user_id, username, @username or empty
        args = (event.pattern_match.group(1) or '').strip()
        if args:
            # user ban setting
            text, buttons = await _user_handler(event, args)
        else:
            # banned users list, check/manager all banned users
            text, buttons = await _banned_page_handler(event)
        await event.respond(text, buttons=buttons)

    @client.on(events.CallbackQuery(data=re.compile(b'banned:')))
    @wrapper.event_wrapper()
    async def ban_handler_callback_query(event: events.CallbackQuery.Event, is_admin):
        action, page_number, chat_id = event.data.decode().split(':')
        chat = db.chat_query(chat_id) or Chat(chat_id, 0, DEFAULT_LANG)
        # if chat.status == int(status):
        #     return
        chat.status = 1
        db.chat_insert_replace(chat)
        await event.answer(i18n('$setting_success$'))

        text, buttons = await _banned_page_handler(event, int(page_number))
        await event.edit(text, buttons=buttons)

        # entity = await client.get_entity(int(chat_id))
        # text, buttons = _get_chat_status(event, entity, chat)
        # await event.edit(text, buttons=buttons)

        # notify user about their status
        # try:
        #     notification = '$user_unbanned$' if chat.status else '$user_banned$'
        #     entity = await client.get_entity(chat_id)
        #     await client.send_message(entity=entity, message=i18n(notification, chat.lang_code))
        # except:
        #     pass

    @client.on(events.CallbackQuery(data=re.compile(b'banned_page:')))
    @wrapper.event_wrapper()
    async def ban_handler_callback_query(event: events.CallbackQuery.Event, is_admin):
        action, page_number = event.data.decode().split(':')
        text, buttons = await _banned_page_handler(event, int(page_number))
        await event.edit(text, buttons=buttons)

    @client.on(events.CallbackQuery(data=re.compile(b'ban_user:')))
    @wrapper.event_wrapper()
    async def ban_handler_callback_query(event: events.CallbackQuery.Event, is_admin):
        action, status, chat_id = event.data.decode().split(':')
        chat = db.chat_query(chat_id) or Chat(chat_id, 1, DEFAULT_LANG)
        # if chat.status == int(status):
        #     return
        chat.status = int(status)
        db.chat_insert_replace(chat)
        await event.answer(i18n('$setting_success$'))

        entity = await client.get_entity(int(chat_id))
        text, buttons = _get_chat_status(event, entity, chat)
        await event.edit(text, buttons=buttons)

        # notify user about their status
        # try:
        #     notification = '$user_unbanned$' if chat.status else '$user_banned$'
        #     entity = await client.get_entity(chat_id)
        #     await client.send_message(entity=entity, message=i18n(notification, chat.lang_code))
        # except:
        #     pass
