#!./venv/bin/python3
import sqlite3

import numpy as np
import pandas as pd


def db_init():
    conn = sqlite3.connect("./finances.db")
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type == 'table';", conn
    )
    if tables.name.empty:
        cur = conn.cursor()
        create_table = open("./init.sql").read()
        cur.executescript(create_table)
    return conn


def main():
    conn = db_init()
    # tables = pd.read_sql_query(
    #     "SELECT name FROM sqlite_master WHERE type == 'table';", conn
    # )
    # print(tables)
    # tables = {key: "" for key in tables.name}
    # print(tables)

    num_choices = np.arange(1, 4)
    choice = input(
        """Which would you like to do?
    1) Add hours,
    2) Add check
    3) Add expense(s)
    Choice: """
    )
    while True:
        if not choice.isdigit():
            choice = input("Please choose a valid option number: ")
            continue
        choice = int(choice)
        if choice not in num_choices:
            choice = input("Please choose a valid option number: ")
            continue
        break

    match choice:
        case 1:
            pass
        case 2:
            pass
        case 3:
            pass
        case _:
            print("How did you get here??")
            quit()


if __name__ == "__main__":
    main()
