#!./venv/bin/python3
import sqlite3
import datetime as dt

import numpy as np
import pandas as pd
from pandas.core.dtypes.dtypes import time


def dt_verify(to_change: str, new_type: dt.date | dt.time) -> dt.date | dt.time:
    while True:
        try:
            changed = new_type.fromisoformat(to_change)
            return changed
        except ValueError:
            match new_type:
                case dt.date:
                    to_change = input("Please enter a valid date[YY-MM-DD]: ")
                case dt.time:
                    to_change = input("Please enter a valid timej[HH:MM]: ")
                case _:
                    print("Unsupported type for function dt_verify")
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
    # Initializes needed vars for function
    # i_data is input i_data
    # be_data is back-end data, separated from i_data to ease calculations
    # rate is current pay rate, will probably create separate space in another db
    # TODO: create jobs table in finances.db, modify init.sql
    # TDC: needed columns would probably be:
    #   start_date(primary?)-DATE, rate-FLOAT, pay_schedule-DATE, possibly more
    conn = conn
    cur = conn.cursor()

    def kv_verify(to_verify: dict):
        print()
        for key, val in to_verify.items():
            print(f"{key}: {val}")
        return input("\ndoes this look valid? y/n: ")

    rate = 16.00
    conn = db_init()
    i_data = {
        "day": dt.date,
        "clock-in": dt.time,
        "lunch-out": dt.time,
        "lunch-in": dt.time,
        "clock-out": dt.time,
    }
    be_data = {
        "worked_hours": dt.timedelta,
        "daily_wage": float,
        "check_date": dt.date,
        "expected_check": float,
    }

    # Takes input data from user and verifies for compatibility with db columns
    # db datatypes are specified in init.sql, specifically hours table
    i_data["day"] = input("day[YYYY-MM-DD] (leave empty if today): ")
    if i_data["day"] == "":
        i_data["day"] = dt.date.today()
    else:
        dt_verify(i_data["day"], dt.date)
    for key in list(i_data.keys())[1:]:
        if key in ["lunch-in", "lunch-out"]:
            i_data[key] = input(f"{key} [HH:MM] leave empty if not applicable: ")
            if i_data[key] == "":
                i_data[key] = dt.time(0, 0)
                continue
        else:
            i_data[key] = input(f"{key} [HH:MM]: ")
        i_data[key] = dt_verify(i_data[key], dt.time)

    yn = kv_verify(i_data)
    while yn != "y":
        if yn != "n":
            yn = input("please enter y or n: ")
            continue
        change = input(
            f"""{' | '.join(list(i_data.keys()))}
Which would you like to change? keep empty to keep: """
        )
        if change == "":
            break
        elif change not in i_data.keys():
            continue
        i_data[change] = dt_verify(
            input(f"change {change}[{i_data[change]}] to: "), i_data[change]
        )
        yn = kv_verify(i_data)

    timedelta_convert = [
        dt.datetime.fromisoformat(f"0001-01-01T{val}") - dt.datetime(1, 1, 1)
        for val in i_data.values()
        if type(val) == dt.time
    ]
    be_data["worked_hours"] = (timedelta_convert[3] - timedelta_convert[0]) - (
        timedelta_convert[2] - timedelta_convert[1]
    )
    del timedelta_convert
    if (i_data["lunch-in"] == dt.time(0, 0)) & (i_data["lunch-out"] == dt.time(0, 0)):
        i_data["lunch-in"] = None
        i_data["lunch-out"] = None
    be_data["worked_hours"] = be_data["worked_hours"].total_seconds()
    be_data["daily_wage"] = round(((be_data["worked_hours"] / 3600) * rate), 2)
    be_data["worked_hours"] = dt.time(
        hour=int(be_data["worked_hours"] // 3600),
        minute=int((be_data["worked_hours"] % 3600) // 60),
    )

    entry = pd.read_sql_query(
        sql="SELECT check_date, expected_check FROM hours DESC LIMIT 1;", con=conn
    )
    if entry.check_date.empty:
        be_data["check_date"] = input("When will your next check be[YYYY-MM-DD]?: ")
        be_data["check_date"] = dt_verify(be_data["check_date"], dt.date)
        be_data["expected_check"] = 0.00
    elif i_data["day"] == (entry.check_date[0] - dt.timedelta(weeks=1)):
        print("Rolling into a new pay period.")
        be_data["check_date"] = entry.check_date[0] + dt.timedelta(weeks=2)
        be_data["expected_check"] = 0.00
    else:
        be_data["check_date"] = entry.check_date[0]
    be_data["expected_check"] += be_data["daily_wage"]
    entry = list((i_data | be_data).values())
    cur.execute("INSERT INTO hours VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", entry)


def add_check(conn: sqlite3.Connection):
    pass


def main():
    conn = db_init()

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
            add_check(conn)
        case 3:
            pass
        case _:
            print("How did you get here??")
            quit()


if __name__ == "__main__":
    pass
