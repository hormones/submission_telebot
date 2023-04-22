import asyncio
import os
import re

import yaml
from base import util

import db

__fs = open(os.path.join("i18n.yml"), 'r', encoding="UTF-8")
__data: dict = yaml.safe_load(__fs)

LANGS: dict = __data.setdefault('langs', {})
DEFAULT_LANG: str = next(iter(LANGS))


def i18n(key: str, lang_code: str = None):
    lang_code = get_lang(lang_code)

    data = key
    if len(key) > 2 and key[1:-1] in __data:
        key = key[1:-1]
    if key in __data:
        data = __data[key].get(lang_code)

    matches = re.findall('\$(.*?)\$', data)
    for match in matches:
        data = data.replace(f'${match}$', i18n(match, lang_code), 1)

    if key in __data:
        __data[key][lang_code] = data  # cache result
    return data


def get_lang(lang_code=None):
    if lang_code and lang_code in LANGS.keys():
        return lang_code
    chat_id = util.get_asyncio_params('chat_id')
    if chat_id:
        lang_code = db.chat_code_query(chat_id)
    return lang_code or DEFAULT_LANG


def get_event_lang(event=None):
    if event and hasattr(event.chat, 'lang_code'):
        return event.chat.lang_code.split('-')[0]
    return DEFAULT_LANG


if __name__ == '__main__':
    print('111')
