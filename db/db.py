import logging
import sqlite3

conn = sqlite3.connect("db/students.db")
cur = conn.cursor()
"""
name John
surname Doe
login xdoe1
uid 10012345
year_of_studies 1/2/3...
program OI/ARI/...
type_of_studies bc/ing
"""


def init_db():
    global conn
    global cur
    create_db_table()


def create_db_table():
    cur.execute("""
                CREATE TABLE students(
                login text, 
                uid integer, 
                year_of_studies integer, 
                program text, 
                type_of_studies text
                )""")
    conn.commit()
    conn.close()


# checks whether record with given uid exists
def check_for_existing_uid(uid):
    query = "SELECT * FROM students WHERE uid = ?"
    data = [uid]

    cur.execute(query, data)
    student = cur.fetchall()

    if len(student) == 0:
        return False
    return True


def insert_new_student(student):
    if check_for_existing_uid(student.uid):
        logging.warning("Someone tried verified with uid that is already in the table: " + student.login + " " + str(student.uid))
        return

    query = """INSERT INTO students VALUES(?, ?, ?, ?, ?)"""
    data = [student.login, student.uid, student.year_of_studies, student.program, student.type_of_studies]
    cur.execute(query, data)
