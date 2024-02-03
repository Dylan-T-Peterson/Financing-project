#!./venv/bin/python3
import sqlite3
import datetime

import numpy as np
import pandas as pd
from pandas._libs.tslibs.parsing import DateParseError


def yn_verify(data: dict):
    while True:
        change = input(
            f"{data}\nWhich would you like to change? keep empty to continue: "
        )
        change_type = type(data[change])
        if change == "":
            break
        if change not in data.keys():
            continue
        try:
            data[change] = change_type(input(f"replace {change}: "))
            print(change, change_type)
        except Exception as e:
            print(e)
            quit()


def db_init():
    conn = sqlite3.connect("./finances.db")
    tables = pd.read_sql_query(
        sql="SELECT name FROM sqlite_master WHERE type == 'table';", con=conn
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
    # Initializes needed vars for function
    # i_data is input i_data
    # be_data is back-end data, separated from i_data to ease calculations
    # rate is current pay rate, will probably create separate space in another db
    # TODO: create jobs table in finances.db, modify init.sql
    # TDC: needed columns would probably be:
    #   start_date(primary?)-DATE, rate-FLOAT, pay_schedule-DATE, possibly more
    rate = int
    conn = db_init()
    i_data = {
        "day": datetime.date,
        "clock-in": pd.Timestamp,
        "lunch-out": pd.Timestamp,
        "lunch-in": pd.Timestamp,
        "clock-out": pd.Timestamp,
    }
    be_data = {
        "worked": pd.Timedelta,
        "check-cutoff": datetime.date.fromisoformat("20240125"),
        "check-date": datetime.date.fromisoformat("20240216"),
        "expected-check": float,
    }

    # Takes i_data from user and verifies for compatibility with db columns
    # db datatypes are specified in init.sql, specifically hours table
    i_data["day"] = input("day[YYYY-MM-DD] (leave empty if today): ")
    if i_data["day"] == "":
        i_data["day"] = datetime.date.today()
    for x in list(i_data.keys())[1:]:
        i_data[x] = input(f"{x} [HH:MM]: ")
        while True:
            if x == "":
                i_data[x] = input("Please enter a time [HH:MM]: ")
                continue
            try:
                i_data[x] = pd.Timestamp(f"{i_data['day']}T{i_data[x]}")
                break
            except DateParseError as e:
                print(type(e))
                i_data[x] = input(f"Invalid format, retry {x}[HH:MM]: ")
    while True:
        for k, v in dict(list(i_data.items())[:5]).items():
            print(f"{k}: {v}")
        match input("does this look valid? y/n: "):
            case "n":
                yn_verify(i_data)
            case "y":
                break
            case _:
                continue

    # Start calculating be_data
    # worked is diff of punched hours
    # expected-check is += previous expected-check
    #   unless condition met (currently 8 days before check_date)
    # TODO: create calculation to update check_cutoff/expected-check
    # TDC: possibly find way to calculate where check_cutoff not needed
    be_data["worked"] = (i_data["clocked-out"] - i_data["clock-in"]) - (
        i_data["lunch-out"] - i_data["lunch-in"]
    )
    be_data["expected-check"] = (be_data["worked"].seconds / 3600) * rate
    # ref_dates = pd.read_sql_query(
    #     sql="SELECT check_cutoff, check_date FROM hours by day DESC LIMIT 1", con=conn
    # )
    # for x in list(be_data.keys())[6:8]:
    #     print(ref_dates)

    # TODO: create checkdate and expected check values
    # TODO: create guard clause if today check_cutoff
    # check date should check for certain daysproperty
    # (probably start with initial payday)
    # expected check should be easy; if check_date == prev check_date
    # expected check += prev expected check
