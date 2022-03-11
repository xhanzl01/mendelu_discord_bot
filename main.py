import logging
import sqlite3

from bot import bot
from db import db

if __name__ == '__main__':
    try:
        db.init_db()
        logging.debug("Creating table and inserting data")
    except sqlite3.OperationalError:
        logging.debug("Table is already created")
    except Exception as ex:
        logging.error("Unspecified error has occurred: " + str(ex))


    bot.start_bot()
