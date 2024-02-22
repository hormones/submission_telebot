import logging
import os
import typing
import python_socks

import yaml
from telethon import TelegramClient
from telethon.tl import types

from base import util
from base.types import TelethonFilter

__fs = open(os.path.join("config.yml"), 'r', encoding="UTF-8")
__config: dict = yaml.safe_load(__fs)

DEBUG: bool = util.get_config(__config, 'debug', False)
APPROVE: bool = util.get_config(__config, 'approve', True)
USER_COMMAND_KEYS: typing.List[str] = util.get_config(__config, 'user_commands', ["start", "lang", "help"])
SHOW_BOT: bool = util.get_config(__config, 'show_bot', True)
SHOW_CHANNEL: bool = util.get_config(__config, 'show_channel', True)
VERSION: str = util.get_config(__config, 'version', "DEV")
# APPROVE_OUTTIME = util.get_config(__config, 'approve_outtime', 1440)
# TIMEOUT_STRATEGY = util.get_config(__config, 'timeout_strategy', 1)

__logging_format = '%(asctime)s %(name)s %(process)d %(filename)s:%(lineno)s %(levelname)s: %(message)s'
__logging_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format=__logging_format, level=__logging_level)
LOGGING = logging.getLogger()
LOGGING_FILE = logging.FileHandler('appdata/submission_telebot.log')
LOGGING_FILE.setLevel(__logging_level)
LOGGING_FILE.setFormatter(logging.Formatter(__logging_format))
LOGGING_FILE.addFilter(TelethonFilter())
LOGGING.addHandler(LOGGING_FILE)

API_ID = util.get_config(__config, 'api_id')
API_HASH = util.get_config(__config, 'api_hash')
BOT_TOKEN = util.get_config(__config, 'bot_token')

# proxy configs
PROXY: bool = util.get_config(__config, 'proxy', False)
PROXY_TYPE = util.get_config(__config, 'proxy_type', 'socks5')
PROXY_ADDR = util.get_config(__config, 'proxy_addr', '127.0.0.1')
PROXY_PORT = util.get_config(__config, 'proxy_port', 1080)
PROXY_USERNAME = util.get_config(__config, 'proxy_username', '')
PROXY_PASSWORD = util.get_config(__config, 'proxy_password', '')

__super_admins: list = util.get_config(__config, 'super_admins')
# super admin id list
SUPER_ADMINS: list = []

APPROVE_CHANNEL: types.Channel = None
APPROVE_GROUP: typing.Union[types.Chat, types.Dialog] = None
SUBMISSION_CHANNEL: types.Channel = None
BOT = None

logging.info(f'=== api_id: {API_ID} ===')
logging.info(f'=== super_admins: {__super_admins} ===')
logging.info(f'=== proxy: {PROXY} ===')
if (PROXY):
    logging.info(f'=== proxy_type: {PROXY_TYPE} ===')
    logging.info(f'=== proxy_addr: {PROXY_ADDR} ===')
    logging.info(f'=== proxy_port: {PROXY_PORT} ===')
    logging.info(f'=== proxy_username: {PROXY_USERNAME} ===')
    logging.info(f'=== proxy_password: {PROXY_PASSWORD} ===')

proxy = {
    'proxy_type': util.find_enum_by_string(python_socks.ProxyType, PROXY_TYPE),
    'addr': PROXY_ADDR,             # (mandatory) proxy IP address
    'port': PROXY_PORT,             # (mandatory) proxy port number
    'username': PROXY_USERNAME,     # (optional) username if the proxy requires auth
    'password': PROXY_PASSWORD,     # (optional) password if the proxy requires auth
    'rdns': True                    # (optional) whether to use remote or local resolve, default remote
}

client = TelegramClient('./appdata/submission_telebot.session', API_ID, API_HASH,
                        proxy=proxy if PROXY else None).start(bot_token=BOT_TOKEN)


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
