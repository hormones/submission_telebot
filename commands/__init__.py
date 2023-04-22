import logging

from . import __common__, ban, setting, help, lang, reply, feedback


async def chat_check(event, key=None):
    '''
    shortcut for __common__.chat_check, provide for other modules
    check if chat is banned and command is allowed
    '''
    return await __common__.chat_check(event, key)


async def init():
    await __common__.init()
    await help.init()
    await lang.init()
    await reply.init()
    await ban.init()
    await setting.init()
    await feedback.init()

    logging.info("=== commands initialized ===")
