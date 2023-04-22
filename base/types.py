import json
import logging


class MyJSONEncoder(json.JSONEncoder):
    '''
    json encoder
    '''

    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return super().default(obj)


class TelethonFilter(logging.Filter):
    '''
    filter out telethon debug logs
    '''

    def filter(self, record):
        return not (record.name.startswith('telethon') and record.levelno == logging.DEBUG)


class Submission(object):
    '''
    Submission object
    '''

    def __init__(self, id=None, sender_id=None, message_id=None, offset=1, anonymous=1,
                 approval_id=None, approver_id=None, approval_result=None, approval_reply_id=None, create_time=None):
        self.id: int = id
        # who send the submission
        self.sender_id: int = sender_id
        # the message id of the submission, in case of album, it's the first message id
        self.message_id: int = message_id
        # the offset of the submission, 1 for single message, else for album
        self.offset: int = offset
        # whether the submission is anonymous
        self.anonymous: int = anonymous
        # the message id of submission forwoard in the approval channel
        self.approval_id: int = approval_id
        # the approver id who approved the submission
        self.approver_id: int = approver_id
        # the result of the approval, 1 for passed, 0 for rejected
        self.approval_result: int = approval_result
        # the message id of submission forward in the approval group, which group linked to the approval channel
        self.approval_reply_id: int = approval_reply_id
        self.create_time: str = create_time

    @property
    def isAlbum(self):
        return self.offset != 1

    @property
    def getParam(self):
        return f'{self.id}|{self.sender_id}|{self.message_id}|{self.offset}|{self.anonymous}'

    def __str__(self):
        return json.dumps(self.__dict__)

    def __json__(self):
        return json.dumps(self.__dict__)


class Chat(object):
    '''
    Chat object
    '''

    def __init__(self, chat_id, status=None, lang_code=None, create_time=None):
        self.chat_id = chat_id
        self.status = status
        self.lang_code = lang_code
        self.create_time: str = create_time

    def __str__(self):
        return json.dumps(self.__dict__)

    def __json__(self):
        return json.dumps(self.__dict__)
