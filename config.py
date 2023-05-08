import logging
import os
import typing

import yaml
from telethon import TelegramClient
from telethon.tl import types

from base import util
from base.types import TelethonFilter

__fs = open(os.path.join("config.yml"), 'r', encoding="UTF-8")
__config: dict = yaml.safe_load(__fs)

DEBUG: bool = util.get_config(__config, 'debug', False)
APPROVE: bool = util.get_config(__config, 'approve', True)
USER_COMMAND_KEYS: list[str] = util.get_config(__config, 'user_commands', ["start", "lang", "help"])
SHOW_BOT: bool = util.get_config(__config, 'show_bot', True)
SHOW_CHANNEL: bool = util.get_config(__config, 'show_channel', True)
VERSION: str = util.get_config(__config, 'version', "DEV")
# APPROVE_OUTTIME = util.get_config(__config, 'approve_outtime', 1440)
# TIMEOUT_STRATEGY = util.get_config(__config, 'timeout_strategy', 1)

__logging_format = '%(asctime)s %(name)s %(process)d %(filename)s:%(lineno)s %(levelname)s: %(message)s'
__logging_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format=__logging_format, level=__logging_level)
LOGGING = logging.getLogger()
LOGGING_FILE = logging.FileHandler('submission_telebot.log')
LOGGING_FILE.setLevel(__logging_level)
LOGGING_FILE.setFormatter(logging.Formatter(__logging_format))
LOGGING_FILE.addFilter(TelethonFilter())
LOGGING.addHandler(LOGGING_FILE)

API_ID = util.get_config(__config, 'api_id')
API_HASH = util.get_config(__config, 'api_hash')
BOT_TOKEN = util.get_config(__config, 'bot_token')

__super_admins: list = util.get_config(__config, 'super_admins')
# super admin id list
SUPER_ADMINS: list = []

APPROVE_CHANNEL: types.Channel = None
APPROVE_GROUP: typing.Union[types.Chat, types.Dialog] = None
SUBMISSION_CHANNEL: types.Channel = None
BOT = None

client = TelegramClient('submission_telebot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


async def _get_manager_entity(config_key, private: bool):
    key = util.get_config(__config, config_key)
    entity = await client.get_entity(key)
    if not isinstance(entity, (types.Channel, types.Chat)):
        raise TypeError(f'entity is not channel or group: {config_key} = {key}')
    # check private for channel and group
    if private and entity.username:
        raise ValueError(f'entity must be private: {config_key} = {key}')
    return entity


async def init():
    global SUPER_ADMINS, APPROVE_CHANNEL, APPROVE_GROUP, SUBMISSION_CHANNEL, BOT
    for key in __super_admins:
        entity = await client.get_entity(key)
        SUPER_ADMINS.append(entity.id)

    APPROVE_CHANNEL = await _get_manager_entity('approve_channel', True)
    APPROVE_GROUP = await _get_manager_entity('approve_group', True)
    SUBMISSION_CHANNEL = await _get_manager_entity('submission_channel', False)
    BOT = await client.get_me()

    logging.info(f'=== config initialized ===')

if __name__ == '__main__':
    print('=====')
