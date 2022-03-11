import logging
import sqlite3

from bot.bot import start_bot
from bot.commands import init_commands
from db import db
if __name__ == '__main__':
    try:
        db.init_db()
        logging.info("Creating table and inserting data")
    except sqlite3.OperationalError:
        logging.info("Table is already created")
    except Exception as ex:
        logging.error("Unspecified error has occurred: " + str(ex))

    init_commands()
    # start_bot()
