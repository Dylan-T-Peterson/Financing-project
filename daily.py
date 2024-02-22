#!./venv/bin/python3
import sqlite3
import datetime as dt

import numpy as np
import pandas as pd


def kv_verify(to_verify: dict):
    print()
    for key, val in to_verify.items():
        print(f"{key}: {val}")
    yn = input("does this look valid? y/n: ")
    while yn != "y":
        if yn != "n":
            yn = input("please enter y or n: ")
            continue
        change = input(
            f"""{' | '.join(list(to_verify.keys()))}
                Which would you like to change? keep empty to keep: """
        )
        if change == "":
            break
        elif change not in to_verify.keys():
            continue
        to_verify[change] = input_verify(
            input(f"change {change}[{to_verify[change]}] to: "), type(to_verify[change])
        )


def choice_verify(choice: str, valid_choices: dict[int, str]):
    while True:
        try:
            if int(choice) in valid_choices.keys():
                return int(choice)
            else:
                for key, var in valid_choices.items():
                    print(f"{key}) {var}")
                choice = input("Please choose a valid option: ")
        except ValueError:
            choice = input("Please choose a valid number: ")
            continue
        except Exception as e:
            raise Exception(f"an error[{e}] has occurred, please contact me with it.")


def input_verify(to_change: str, new_type: type):
    while True:
        match new_type:
            case dt.date | dt.time:
                try:
                    changed = new_type.fromisoformat(to_change)
                    return changed
                except ValueError:
                    if new_type == dt.date:
                        to_change = input("Please enter a valid date[YYYY-MM-DD]: ")
                        continue
                    if new_type == dt.time:
                        to_change = input("Please enter a valid time[HH:MM]: ")
                        continue
                except Exception as e:
                    raise Exception(
                        f"{e}\nHow did you get here?? Contact me with the error."
                    )
            case _:
                try:
                    changed = new_type(to_change)
                    return changed
                except ValueError:
                    to_change = input(
                        f"""Please enter a valid {str(new_type).split("'")[1]}: """
                    )
                except Exception as e:
                    raise Exception(
                        f"{e}\nHow did you get here?? Contact me with the error."
                    )


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
    RATE = pd.read_sql_query(
        sql="SELECT hourly_wage FROM job_info DESC LIMIT 1;", con=conn
    )
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
        input_verify(i_data["day"], dt.date)
    for key in list(i_data.keys())[1:]:
        if key in ["lunch-in", "lunch-out"]:
            i_data[key] = input(f"{key} [HH:MM] leave empty if not applicable: ")
            if i_data[key] == "":
                i_data[key] = dt.time(0, 0)
                continue
        else:
            i_data[key] = input(f"{key} [HH:MM]: ")
        i_data[key] = input_verify(i_data[key], dt.time)
    kv_verify(i_data)

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
    be_data["daily_wage"] = round(((be_data["worked_hours"] / 3600) * RATE), 2)
    be_data["worked_hours"] = dt.time(
        hour=int(be_data["worked_hours"] // 3600),
        minute=int((be_data["worked_hours"] % 3600) // 60),
    )

    entry = pd.read_sql_query(
        sql="SELECT check_date, expected_check FROM hours DESC LIMIT 1;", con=conn
    )
    if entry.check_date.empty:
        be_data["check_date"] = input("When will your next check be[YYYY-MM-DD]?: ")
        be_data["check_date"] = input_verify(be_data["check_date"], dt.date)
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
    conn = conn
    cur = conn.cursor()
    i_data = {
        "check_date": dt.date,
        "normal_hours": dt.time,
        "ot_hours": dt.time,
        "gross_income": float,
        "tax": float,
        "post_tax_deduction": float,
        "net_income": float,
        "notes": str,
    }
    i_data["check_date"] = input_verify(
        input("What is the date of your check?"), dt.date
    )
    for key in list(i_data.keys())[1:3]:
        i_data[key] = input_verify(
            input(f'How many {key.replace("_"," ")} from this check?: '), dt.time
        )
    for key in list(i_data.keys())[3:7]:
        i_data[key] = input_verify(
            input(f'How much {key.replace("_"," ")} for this check?: '), float
        )
    i_data["notes"] = input("Any notes for this check?: ")
    if i_data["notes"] == "":
        i_data["notes"] = None
    entry = list((i_data).values())
    cur.execute("INSERT INTO paychecks VALUES(?, ?, ?, ?, ?, ?, ?, ?)", entry)


def add_expenses(conn: sqlite3.Connection):
    conn = conn
    cur = conn.cursor()
    ANNUAL = 57_000
    # ANNUAL = pd.read_sql_query(
    #     sql="SELECT annual_wage FROM job_info DESC LIMIT 1;", con=conn
    # )
    VALID_CHOICES = {1: "Bills", 2: "Expenses"}
    i_data = {
        "name": str,
        "frequency": str,
        "due_date": dt.date,
        "cost": float,
    }
    be_data = {
        "yearly_cost": float,
        "percent_annual": float,
    }

    for key, var in VALID_CHOICES.items():
        print(f"{key}) {var}")
    choice = input("what are you looking to input?: ")
    choice = VALID_CHOICES[choice_verify(choice, VALID_CHOICES)].lower()

    i_data["name"] = input(f"What is the name of the {choice[:-1]}?: ")
    while i_data["frequency"] not in ["a", "m", "b", "w"]:
        i_data["frequency"] = input(
            f"""(a)nnually, (m)onthly, (b)i-weekly, or (w)eekly
        What is the frequency of the {choice[:-1]}?: """
        )
    i_data["due_date"] = input_verify(
        input(f"When is this {choice[:-1]} due?: "), dt.date
    )
    i_data["cost"] = input_verify(input(f"How much is the {choice[:-1]}?: "), float)

    match i_data["frequency"]:
        case "a":
            be_data["yearly_cost"] = i_data["cost"]
        case "m":
            be_data["yearly_cost"] = i_data["cost"] * 12
        case "b":
            be_data["yearly_cost"] = i_data["cost"] * 26
        case "w":
            be_data["yearly_cost"] = i_data["cost"] * 52
        case _:
            raise Exception("how did you get here??")
    be_data["yearly_cost"] = round(be_data["yearly_cost"], 2)
    be_data["percent_annual"] = round(be_data["yearly_cost"] / ANNUAL, 3)

    entry = i_data | be_data
    # for key, var in entry.items():
    #     print(f"{key}: {var}")
    cur.execute(f"INSERT INTO {choice} VALUES(?, ?, ?, ?, ?, ?)", entry)


def main():
    CHOICES = {
        1: "Add hours",
        2: "Add check",
        3: "Add expense(s)",
    }
    conn = db_init()

    for key, var in CHOICES.items():
        print(f"{key}) {var}")
    choice = input("Which would you like to do?:")
    choice = choice_verify(choice, CHOICES)

    match choice:
        case 1:
            add_hours(conn)
        case 2:
            add_check(conn)
        case 3:
            add_expenses(conn)
        case _:
            raise Exception("How did you get here??")


# TODO: test add_check and add_expenses
if __name__ == "__main__":
    pass
