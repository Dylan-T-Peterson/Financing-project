#!./venv/bin/python3
import sqlite3
import datetime

import numpy as np
import pandas as pd


def yn_verify(data: dict):
    while True:
        change = input(
            f"{data}\nWhich would you like to change? keep empty to continue: "
        )
        if change == "":
            break
        if change not in data.keys():
            continue
        data[change] = input(f"replace {change}: ")


def db_init():
    conn = sqlite3.connect("./finances.db")
    tables = pd.read_sql_query(
        sql="SELECT name FROM sqlite_master WHERE type == 'table';",
        con=conn
    )
    if tables.name.empty:
        cur = conn.cursor()
        create_table = open("./init.sql").read()
        cur.executescript(create_table)
    return conn


def add_hours(conn: sqlite3.Connection):
    pass


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
            add_hours(conn)
        case 2:
            pass
        case 3:
            pass
        case _:
            print("How did you get here??")
            quit()


if __name__ == "__main__":
    conn = db_init()
    data = {
        "day": datetime.date,
        "clock-in": pd.Timestamp,
        "lunch-out": pd.Timestamp,
        "lunch-in": pd.Timestamp,
        "clock-out": pd.Timestamp,
        'worked': pd.Timedelta,
        'check-date': datetime.date,
        'expected-check': float
    }
    data["day"] = input("day[YYYY-MM-DD] (leave empty if today): ")
    if data["day"] == "":
        data["day"] = datetime.date.today()

    print(data["day"])
    for x in list(data.keys())[1:]:
        data[x] = input(f"{x}[HH:MM]: ")
        while True:
            try:
                data[x] = pd.Timestamp(f"{data['day']}T{data[x]}")
                break
            except:
                data[x] = input(f"Invalid format, retry {x}[HH:MM]: ")
    while True:
        print(data)
        match input("does this look valid? y/n: "):
            case "n":
                yn_verify(data)
            case "y":
                break
            case _:
                continue

    data['worked'] = ((data['clocked-out'] - data['clock-in'])
                      - (data["lunch-out"] - data["lunch-in"]))
    # TODO: create checkdate and expected check values
    # check date should check for certain daysproperty
    # (probably start with initial payday)
    # expected check should be easy; if check_date == prev check_date
    # expected check += prev expected check
