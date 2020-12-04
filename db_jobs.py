import sqlite3
from tabulate import tabulate

CREATE_TABLE = '''CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    link TEXT)
               '''

INSERT_JOB = '''INSERT INTO jobs (title, company, location, link) VALUES (:title, :company, :location, :link)'''

DISPLAY_JOBS = '''SELECT id, title, company, location FROM jobs'''

GET_LINK = '''SELECT link FROM jobs WHERE id = (:id)'''

CLEAR_ALL = '''DELETE FROM jobs'''


def connect():
    return sqlite3.connect("jobs.db")


def create_table(connection):
    with connection:
        connection.execute(CREATE_TABLE)


def insert_job(connection, cursor, title, company, location, link):
    with connection:
        cursor.execute(INSERT_JOB, {"title": title, "company": company, "location": location, "link": link})


def display_jobs(cursor):
    cursor.execute(DISPLAY_JOBS)
    jobs = tabulate(cursor.fetchall(), headers=["Id", "Title", "Company", "Location"])
    return jobs


def get_link(cursor, n):
    cursor.execute(GET_LINK, {"id": n})
    link = cursor.fetchall()
    return link


def clear_all(connection, cursor):
    with connection:
        cursor.execute(CLEAR_ALL)
