from telethon import events

import config
import db
import wrapper
from base import util
from config import client
from i18n import i18n

from . import __common__


async def init():
    '''
    command useage: /statistics
    '''
    @client.on(events.NewMessage(pattern='/statistics( .*)?', incoming=True))
    @wrapper.event_wrapper('statistics')
    async def command_statistics_handler(event, is_admin):
        '''
        command useage: /statistics
        '''
        if not is_admin:
            return

        statistics_text = ''
        # statistics daily
        result = db.submission_statistics('day')
        statistics_text += i18n('$statistics_display_daily$').format(
            result[0], result[1] or 0, result[2] or 0, result[3] or 0, result[4] or 0
        )

        # statistics monthly
        result = db.submission_statistics('month')
        statistics_text += '\n\n' + i18n('$statistics_display_monthly$').format(
            result[0], result[1] or 0, result[2] or 0, result[3] or 0, result[4] or 0
        )

        # statistics yearly
        result = db.submission_statistics('year')
        statistics_text += '\n\n' + i18n('$statistics_display_yearly$').format(
            result[0], result[1] or 0, result[2] or 0, result[3] or 0, result[4] or 0
        )

        # statistics total
        result = db.submission_statistics()
        statistics_text += '\n\n'+i18n('$statistics_display_total$').format(
            result[0], result[1] or 0, result[2] or 0, result[3] or 0, result[4] or 0
        )

        await event.respond(statistics_text)
