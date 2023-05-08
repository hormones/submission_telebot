import logging

from . import __common__, ban, feedback, help, lang, reply, setting

ALL_COMMANDS = __common__.ALL_COMMANDS


async def init():
    await __common__.init()
    await help.init()
    await lang.init()
    await reply.init()
    await ban.init()
    await setting.init()
    await feedback.init()

    logging.info("=== commands initialized ===")
