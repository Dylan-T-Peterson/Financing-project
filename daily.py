#!./venv/bin/python3
import sqlite3
import datetime as dt

import numpy as np
import pandas as pd


def dtype_verify(to_change: str, new_type: dt.date | dt.time) -> dt.date | dt.time:
    while True:
        try:
            changed = new_type.fromisoformat(to_change)
            return changed
        except ValueError:
            match new_type:
                case dt.date:
                    to_change = input("Please enter a valid date[YY-MM-DD]: ")
                case dt.time:
                    to_change = input(f"Invalid format, retry {x}[HH:MM]: ")
                case _:
                    print("Unsupported type for function dtype_verify")
                    quit()
        except Exception as e:
            print(f"{e}\nHow did you get here?? Contact me with the error.")
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
    rate = float
    conn = db_init()
    i_data = {
        "day": dt.date,
        "clock-in": dt.time,
        "lunch-out": dt.time,
        "lunch-in": dt.time,
        "clock-out": dt.time,
    }
    be_data = {
        "worked": dt.timedelta,
        "check-date": dt.date,
        "expected-check": float,
    }

    # Takes i_data from user and verifies for compatibility with db columns
    # db datatypes are specified in init.sql, specifically hours table
    i_data["day"] = input("day[YYYY-MM-DD] (leave empty if today): ")
    if i_data["day"] == "":
        i_data["day"] = dt.date.today()
    else:
        dtype_verify(i_data["day"], dt.date)
    for x in list(i_data.keys())[1:]:
        i_data[x] = input(f"{x} [HH:MM]: ")
        dtype_verify(i_data[x], dt.time)

    for key, val in i_data.items():
        print(f"{key}: {val}")
    x = input("does this look valid? y/n: ")
    while x != "y":
        change = input(
            f"{i_data}\nWhich would you like to change? keep empty to keep: "
        )
        if change == "":
            break
        if change not in i_data.keys():
            continue
        dtype_verify(change, type(i_data[change]))
        x = input("does this look valid? y/n: ")

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
