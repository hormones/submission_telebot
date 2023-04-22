import logging

import commands
import config
import db
import submission
from config import client


async def main():
    db.init()
    await config.init()
    await commands.init()
    submission.init()
    logging.info('=== STARTED SUCCESS ===')

    await client.run_until_disconnected()
    db.close()
    logging.info('=== STOPPED SUCCESS ===')

with client:
    client.loop.run_until_complete(main())
