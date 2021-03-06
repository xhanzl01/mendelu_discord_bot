import logging
import sqlite3
import sys

from bot.bot import init_bot

from db import db

# TODO put everything into try catch blocks and log errors into file

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.basicConfig(level=logging.CRITICAL, filename="logger.log", filemode="w",
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=logging.ERROR, filename="logger.log", filemode="w",
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    try:
        db.init_db()
        logging.info("Creating table and inserting data")
    except sqlite3.OperationalError:
        logging.info("Table is already created")
    except Exception as ex:
        logging.error("Unspecified error has occurred: " + str(ex))

    init_bot()

