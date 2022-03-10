import logging
import sqlite3
from student import Student
from verification import send_mail

from db import db


if __name__ == '__main__':
    try:
        db.init_db()
        logging.debug("Creating table and inserting data")
    except sqlite3.OperationalError:
        logging.debug("Table is already created")
    except Exception as ex:
        logging.error("Unspecified error has occurred: " + str(ex))

    send_mail("petrhanzl33@gmail.com", 111456848648486648)

