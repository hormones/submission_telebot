import logging

from telethon import events

import config
import db
import wrapper
from config import client
from i18n import DEFAULT_LANG, i18n

from . import __common__


def _save_reply_id(message):
    if not message.forward or not message.forward.channel_post:
        return
    approval_id = message.forward.channel_post
    logging.debug(f'new linked message: {message.id} by approved: {approval_id}')
    if db.submission_exists_by_approval_id(approval_id):
        db.submission_update_by_approval_id({'approval_id': approval_id, 'approval_reply_id': message.id})

async def init():
    @client.on(events.NewMessage(chats=config.APPROVE_GROUP, pattern='/reply( .*)?', func=lambda e: e.is_reply, incoming=True))
    @wrapper.event_wrapper('reply')
    async def command_reply_handler(event, is_admin):
        '''
        command useage: /reply reply_text
        '''
        reply_text = (event.pattern_match.group(1) or '').strip()
        if not reply_text:
            return
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.forward and reply_message.forward.channel_post:
            approval_id = reply_message.forward.channel_post
            logging.debug(f'comments to approval_id: {approval_id}')
            submission = db.submission_query_by_approval_id(approval_id)
            if not submission:
                logging.error(f'cannot send reply for approval_id: {approval_id}, submission does not exist')
                return
            lang_code = db.chat_query(submission.sender_id).lang_code or DEFAULT_LANG
            reply_text = i18n('$command_reply_comments$', lang_code).format(reply_text)
            await client.send_message(entity=submission.sender_id, message=reply_text, reply_to=submission.message_id)

    @client.on(events.NewMessage(chats=config.APPROVE_GROUP, func=lambda e: not e.is_reply and not e.grouped_id, incoming=True))
    @wrapper.event_wrapper()
    async def command_reply_handler(event, is_admin):
        '''
        single message handler,
        save linked message id to db by approval channel
        useage: record approval result when approve or reject
        '''
        _save_reply_id(event.message)

    @client.on(events.Album(chats=config.APPROVE_GROUP, func=lambda e: not e.is_reply))
    @wrapper.event_wrapper()
    async def command_reply_album_handler(event, is_admin):
        '''
        album handler,
        save linked message id to db by approval channel
        useage: record approval result when approve or reject
        '''
        _save_reply_id(event.messages[0])