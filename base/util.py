import asyncio
import base64
import json
import logging
import os
from typing import TypeVar

from base.types import MyJSONEncoder, Submission

T = TypeVar('T')


def dumps(jsonobject):
    '''
    json dumps with custom encoder, special util for object
    '''
    return json.dumps(jsonobject, cls=MyJSONEncoder).replace("\\", "").replace("\"{", "{").replace("}\"", "}")


def b64encode(value):
    if isinstance(value, str):
        return base64.b64encode(value.encode()).decode()
    else:
        json_str = dumps(value)
        return base64.b64encode(json_str.encode()).decode()


def b64decode(value, clazz: T) -> T:
    decoded = base64.b64decode(value.encode()).decode()
    return json.loads(decoded, object_hook=clazz)


def submission_loads(data: str) -> Submission:
    '''
    load submission from string
    '''
    id, sender_id, message_id, offset, anonymous = data.split('|')
    return Submission(
        id=int(id),
        sender_id=int(sender_id),
        message_id=int(message_id),
        offset=int(offset),
        anonymous=int(anonymous))


def parse_bool(value):
    '''
    parse bool value
    '''
    if isinstance(value, str):
        return value.lower() not in ['false', '0']
    elif isinstance(value, bool):
        return value
    else:
        return bool(value)


def get_config(dic: dict, key: str, default=None):
    '''
    get config value
    step 1: try to get value from env
    step 2: try to get value from config
    step 3: return default value
    '''
    value = os.environ.get(key)
    if value is None:
        if key not in dic and default is None:
            raise ValueError(f'config key not found: {key}')
        value = dic.get(key, default)
    return value


def get_asyncio_params(key):
    '''
    get asyncio task event params
    '''
    task = asyncio.current_task()
    if not hasattr(task, key):
        logging.warn(f"[{task.get_name()}] get param from task: {key} = None")
        return None
    return getattr(task, key, None)
