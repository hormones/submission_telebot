import logging
import sqlite3
import typing

from base import util
from base.types import Chat, Submission

_conn: sqlite3.Connection = None


def init():
    global _conn
    _conn = sqlite3.connect('appdata/submission_telebot.db')

    table_exists = _conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat';").fetchone()
    if table_exists is None:
        logging.info('create table --> submission chat')
        _conn.execute('''CREATE TABLE submission
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sender_id   INTEGER   NOT NULL,
                            message_id  INTEGER   NOT NULL,
                            offset      INTEGER DEFAULT 1,
                            anonymous   INTEGER DEFAULT 1,
                            approval_id  INTEGER,
                            approver_id  INTEGER,
                            approval_result  INTEGER,
                            approval_reply_id INTEGER,
                            create_time DATETIME DEFAULT CURRENT_TIMESTAMP);''')
        # status 1/0 normal/banned
        _conn.execute('''CREATE TABLE chat
                           (chat_id     INTEGER   PRIMARY KEY,
                            status      INTEGER   DEFAULT 1,
                            lang_code   TEXT,
                            create_time DATETIME DEFAULT CURRENT_TIMESTAMP);''')

    logging.info(f'=== database initialized ===')


def close():
    _conn.close()


def _insert(table: str, obj: dict, type: str = None):
    logging.debug(f'INSERT {type} --> table: {table} obj: {util.dumps(obj)}')
    type = 'OR ' + type.upper() if type else ''
    data = {k: v for k, v in obj.items() if k != 'create_time' and v != None}
    fields = ", ".join(data.keys())
    placeholder = ", ".join(['?' for k in data.keys()])
    params = list(data.values())
    cursor = _conn.cursor()
    sql = f"INSERT {type} INTO {table} ({fields}) VALUES ({placeholder})"
    id = cursor.execute(sql, params).lastrowid
    _conn.commit()
    cursor.close()
    return id


def _update(table: str, obj: dict, key='id'):
    # filter parameters: id and create_time and None-value
    data = {k: v for k, v in obj.items() if (k != key and k != 'create_time' and v != None)}

    set_stmts = [f'{k} = ?' for k in data.keys()]
    params = list(data.values())
    params.append(obj[key])

    sql = f"UPDATE {table} SET {', '.join(set_stmts)} WHERE {key} = ?"
    logging.debug(f'update {table} --> sql: {sql}, data: {util.dumps(obj)}')
    cursor = _conn.cursor()
    rowcount = cursor.execute(sql, params).rowcount
    _conn.commit()
    if not rowcount:
        logging.warning(f'update failed, table: {table}, {key}: {obj[key]}, number of rows affected: {rowcount}')
    cursor.close()


def _query_one_by_field(table: str, field='id', value=None) -> tuple:
    logging.debug(f'query data: {table}.{field} = {value}')
    cursor = _conn.cursor()
    result = cursor.execute(f"SELECT * FROM {table} WHERE {field}=?", (value,)).fetchone()
    cursor.close()
    return result


def _query_all(table: str) -> tuple:
    logging.debug(f'query all: {table}')
    cursor = _conn.cursor()
    result = cursor.execute(f"SELECT * FROM {table} ORDER BY create_time").fetchall()
    cursor.close()
    return result


def _exists(table: str, field='id', value=None) -> bool:
    logging.debug(f'query data exists: {table}.{field} = {value}')
    cursor = _conn.cursor()
    row = cursor.execute(f"SELECT count(1) FROM {table} WHERE {field}=?", (value,)).fetchone()
    cursor.close()
    return True if row[0] else False


def submission_insert_replace(obj: object):
    return _insert('submission', obj.__dict__, 'replace')


def submission_insert_ignore(obj: object):
    return _insert('submission', obj.__dict__, 'ignore')


def submission_update(obj: object):
    _update('submission', obj.__dict__, 'id')


def submission_exists_by_approval_id(approval_id):
    return _exists('submission', 'approval_id', approval_id)


def submission_update_by_approval_id(dic: dict):
    _update('submission', dic, 'approval_id')


def submission_query(id) -> Submission:
    row = _query_one_by_field('submission', 'id', id)
    return Submission(*row) if row else None


def submission_query_by_approval_id(approval_id) -> Submission:
    row = _query_one_by_field('submission', 'approval_id', approval_id)
    return Submission(*row) if row else None


def submission_query_all() -> typing.List[Submission]:
    rows = _query_all('submission')
    return [Submission(*row) for row in rows]


def chat_code_query(chat_id=None) -> str:
    chat = chat_query(chat_id)
    return chat.lang_code if chat else None


def chat_banned(chat_id=None) -> str:
    chat = chat_query(chat_id)
    if not chat:
        return False
    return False if chat.status else True


def chats_count_banned() -> int:
    logging.debug(f'count chats banned')
    cursor = _conn.cursor()
    row = cursor.execute(f"SELECT count(1) FROM chat WHERE status=0").fetchone()
    cursor.close()
    return row[0]


def chats_banned(page_number=1, page_size=10) -> typing.List[Chat]:
    data = []
    offset = (page_number - 1) * page_size
    logging.debug(f'query chats banned')
    cursor = _conn.cursor()
    total = cursor.execute(f"SELECT count(1) FROM chat WHERE status=0").fetchone()[0]
    if total and offset < total:
        rows = cursor.execute(
            f"SELECT * FROM chat WHERE status=0 ORDER BY create_time LIMIT {page_size} OFFSET {offset}").fetchall()
        data = [Chat(*row) for row in rows]
    cursor.close()
    return (total, data)


def chat_query(chat_id=None) -> Chat:
    row = _query_one_by_field('chat', 'chat_id', chat_id)
    return Chat(*row) if row else None


def chat_insert_replace(obj: Chat) -> int:
    return _insert('chat', obj.__dict__, 'replace')


def chat_insert_ignore(obj: Chat) -> int:
    return _insert('chat', obj.__dict__, 'ignore')


def chat_update(obj: Chat):
    _update('chat', obj.__dict__, 'chat_id')


def chat_query_all() -> typing.List[Chat]:
    rows = _query_all('chat')
    return [Chat(*row) for row in rows]


def chat_exists(chat_id) -> bool:
    return _exists('chat', 'chat_id', chat_id)


def submission_statistics(start=None):
    cursor = _conn.cursor()
    query = """
        SELECT 
            COUNT(*) AS total,
            SUM(CASE WHEN approval_result = 1 THEN 1 ELSE 0 END) AS passed,
            SUM(CASE WHEN approval_result = 0 THEN 1 ELSE 0 END) AS rejected,
            SUM(CASE WHEN approval_result IS NULL THEN 1 ELSE 0 END) AS not_processed,
            ROUND(SUM(CASE WHEN approval_result = 1 THEN 1 ELSE 0 END)*100.0/ COUNT(*), 2) AS passed_rate
        FROM submission
    """

    if start:
        query = f"{query} WHERE create_time >= date('now', 'start of {start}') AND create_time <= datetime('now', 'localtime')"

    result = cursor.execute(query).fetchone()
    cursor.close()
    return result
