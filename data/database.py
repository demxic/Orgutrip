import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('flights.db')
c = conn.cursor()


def eliminate_table():
    c.execute("DROP TABLE flights")

def create_table():
    c.execute("CREATE TABLE flights (date DATE,"
              "number VARCHAR,"
              "origin VARCHAR,"
              "begin VARCHAR,"
              "destination VARCHAR,"
              "duration REAL)")


def enter_dynamic_data():
    c.execute("INSERT INTO flights (date, number) VALUES (?,?)",
              (datetime.now().date(),
               '0403'))
    c.execute("INSERT INTO flights (date, number) VALUES (?,?)",
              (datetime.now().date()+ timedelta(days = 1),
               '0503'))
    conn.commit()


def read_from_database():
    for row in c.execute("SELECT * FROM flights"):
        print(row)

eliminate_table()
create_table()
conn.close()
