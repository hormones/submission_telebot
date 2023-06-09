import logging
import re

from telethon import Button, events

import config
import db
import wrapper
from base import util
from base.types import Submission
from config import client
from i18n import i18n


async def _get_display_message(submission, additional_text=''):
    file = None
    message = None

    # single message
    if submission.offset == 1:
        message = await client.get_messages(entity=submission.sender_id, ids=submission.message_id)
        if additional_text:
            entities = message.entities or []
            a_message, a_entities = await client._parse_message_text((message.raw_text + additional_text), parse_mode='md')
            message.message = a_message
            message.entities = entities + a_entities
    # album
    else:
        ids = [submission.message_id + i for i in range(submission.offset)]
        file = await client.get_messages(entity=submission.sender_id, ids=ids)
        message = file[0].raw_text + additional_text

    return message, file


def _get_additional_text(submission, sender):
    additional_text = i18n("\n\n$submission_via_anonymous$")
    if submission.anonymous == 0:
        additional_text = i18n("\n\n$submission_via_user$").format(sender.first_name, submission.sender_id)

    if config.SHOW_BOT:
        additional_text += i18n("\n$bot_link$").format(config.BOT.first_name, config.BOT.username)

    if config.SHOW_CHANNEL and config.SUBMISSION_CHANNEL.username:
        additional_text += i18n("\n$submission_channel_link$").format(config.SUBMISSION_CHANNEL.title,
                                                                      config.SUBMISSION_CHANNEL.username)
    return additional_text


async def _send_message(entity, message=None, file=None, buttons=[]):
    if file:
        messages = await client.send_file(entity=entity, file=file, caption=message, buttons=buttons)
        if buttons:  # send_file`s buttons setting is not working
            await messages[0].reply("pass?", buttons=buttons)
        return messages[0].id
    else:
        message = await client.send_message(entity=entity, message=message, buttons=buttons)
        return message.id


async def _push_handler(event, is_admin):
    if is_admin:
        return
    message_id = None
    offset = 1
    if event.grouped_id:
        message_id = event.messages[0].id
        offset = (event.messages[-1].id - message_id) + 1
    else:
        message_id = event.id

    submission = Submission(sender_id=event.sender_id, message_id=message_id, offset=offset)
    submission.id = db.submission_insert_replace(submission)
    buttons = [
        [
            Button.inline(i18n('$key_yes$'), f"push:1:{submission.getParam}"),
            Button.inline(i18n('$key_no$'), f"push:0:{submission.getParam}")
        ],
        [Button.inline(i18n('$cancel$'), f"push:-1:{submission.getParam}")],
    ]
    await event.reply(i18n('$is_push_anonymous$'), buttons=buttons)


def init():
    @client.on(events.NewMessage(pattern=r'^(?!/)', func=lambda e: e.is_private and not e.grouped_id))
    @wrapper.event_wrapper()
    async def message_handler(event, is_admin):
        logging.info(f'message_handler: new submission from [{event.sender.first_name}]({event.sender_id}): {event.id}')
        await _push_handler(event, is_admin)

    # muitiple media submission, photos or videos
    @client.on(events.Album(func=lambda e: e.is_private))
    @wrapper.event_wrapper()
    async def album_handler(event, is_admin):
        logging.info(
            f'album_handler: new submission from [{event.sender.first_name}]({event.sender_id}): {event.messages[0].id}')
        await _push_handler(event, is_admin)

    @client.on(events.CallbackQuery(data=re.compile(b'push:')))
    @wrapper.event_wrapper()
    async def push_handler_callback_query(event: events.CallbackQuery.Event, is_admin):
        action, key, data = event.data.decode().split(':')
        logging.debug(f"push button data ---> key: {key}, data: {data}")

        submission = util.submission_loads(data)

        if key == "-1":
            await event.edit(i18n('$cancel_success$'), buttons=None)
            return
        submission.anonymous = int(key)

        if key == "1":
            message = await client.get_messages(entity=event.chat, ids=submission.message_id)
            if message.forward and message.forward.sender_id != event.sender_id:
                await event.answer(i18n('$anonymous_not_allowed$'), alert=True)
                return

        entity = config.SUBMISSION_CHANNEL
        buttons = None

        additional_text = ''
        if config.APPROVE:
            entity = config.APPROVE_CHANNEL
            buttons = [
                [Button.inline(i18n('$pass$'), f"approve:1:{submission.getParam}")],
                [Button.inline(i18n('$reject$'), f"approve:0:{submission.getParam}")]
            ]
        else:
            additional_text = _get_additional_text(submission, event.sender)

        message, file = await _get_display_message(submission, additional_text)

        submission.approval_id = await _send_message(entity, message, file, buttons)

        db.submission_update(submission)

        reply_text = '$to_approve_success$' if config.APPROVE else '$approve_succeeded$'
        await event.edit(i18n(reply_text), buttons=None)

    @client.on(events.CallbackQuery(data=re.compile(b'approve:')))
    @wrapper.event_wrapper()
    async def approve_handler_callback_query(event: events.CallbackQuery.Event, is_admin):
        action, key, data = event.data.decode().split(':')
        logging.debug(f"approve button data ---> key: {key}, data: {data}")

        submission = db.submission_query(data.split('|')[0])
        submission.approver_id = event.sender_id
        submission.approval_result = int(key)
        logging.info(f"submission approved by {event.sender.first_name}: {util.dumps(submission)}")
        db.submission_update_by_approval_id({"approval_id": submission.approval_id,
                                            "approver_id": event.sender_id, "approval_result": int(key)})

        sender = await client.get_entity(submission.sender_id)

        # approval passed, forward to submission channel
        if submission.approval_result:
            additional_text = _get_additional_text(submission, sender)
            message, file = await _get_display_message(submission, additional_text)
            await _send_message(entity=config.SUBMISSION_CHANNEL, message=message, file=file, buttons=[])

        # send approval result to user
        try:
            user_lang_code = db.chat_code_query(submission.sender_id)
            reply_text = '$approve_succeeded$' if submission.approval_result else '$approve_rejected$'
            await client.send_message(entity=sender, message=i18n(reply_text, user_lang_code), reply_to=submission.message_id)
        except Exception as e:
            logging.exception("send approval result to user error: %s", e)

        # clear approval buttons
        await event.edit(buttons=None)

        # log who did this
        # await asyncio.sleep(3)
        log_text = '$approve_succeeded_log$' if submission.approval_result else '$approve_rejected_log$'
        log_text = i18n(log_text).format(event.sender.first_name, event.sender_id)
        await client.send_message(entity=config.APPROVE_GROUP, message=log_text, reply_to=submission.approval_reply_id)

        # got ERROR: The API access for bot users is restricted. The method you tried to invoke cannot be executed as a bot (caused by GetDiscussionMessageRequest)
        # it does not match the official description: https://tl.telethon.dev/methods/messages/get_discussion_message.html
        # await event.respond(log_text, comment_to=event.message_id)

    logging.info('=== push initialized ===')
