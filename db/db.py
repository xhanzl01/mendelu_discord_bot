import csv
import logging
import sqlite3
from config import data_fouss


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
    # global conn
    # global cur
    create_db_table()


def create_db_table():
    cur.execute("""
                CREATE TABLE students(
                name text,
                surname text,
                discord_id text,
                login text, 
                uid integer, 
                year_of_studies integer, 
                program text, 
                verification_token integer, 
                karma integer 
                )""")
    conn.commit()


# checks whether record with given uid exists
def check_for_existing_uid(uid):
    query = "SELECT * FROM students WHERE uid = ?"
    data = [uid]

    cur.execute(query, data)
    student = cur.fetchall()

    if len(student) == 0:
        return False
    return True


def insert_new_student(name, surname, discord_id, login, uid, year_of_studies, program, verification_token):
    query = """INSERT INTO students VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    data = [name, surname, discord_id, login, uid, year_of_studies, program, verification_token, 0]
    cur.execute(query, data)
    conn.commit()


def return_all_students_in_db():
    query = "SELECT * FROM students"
    cur.execute(query)
    students = cur.fetchall()
    return students


def get_student_by_discord_id(discord_id):
    query = "SELECT * FROM students WHERE discord_id = ?"
    data = [discord_id]
    cur.execute(query, data)
    student = cur.fetchall()
    return student


def update_studies(db_row, updated_arg, discord_id_arg):
    query = f"""UPDATE students SET {db_row} = ? WHERE discord_id = ?"""
    data = [updated_arg, discord_id_arg]
    cur.execute(query, data)
    logging.info(f"Student in the db has been updated {get_student_by_discord_id(discord_id_arg)}")
    conn.commit()


def insert_fouss():
    # query = """INSERT INTO students(
    #         name,surname,discord_id,login,uid,year_of_studies, program, verification_token, karma)
    #         VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    #         """
    # cur.execute(query, data_fouss)
    # conn.commit()
    # print(return_all_students_in_db())
    pass


def migrate_old_db_data():
    data_file = open("docs/mendelu_old_db_data.csv")
    rows = csv.reader(data_file)
    cur.executemany("INSERT INTO students VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
