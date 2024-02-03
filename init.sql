CREATE TABLE IF NOT EXISTS hours (
  day DATE PRIMARY KEY,
  clock_in DATETIME NOT NULL,
  lunch_out DATETIME,
  lunch_in DATETIME,
  clock_out DATETIME NOT NULL,
  worked_hours FLOAT NOT NULL,
  check_cutoff DATE NOT NULL,
  check_date DATE NOT NULL,
  expected_check FLOAT NOT NULL
);
CREATE TABLE IF NOT EXISTS paychecks (
  check_id FLOAT PRIMARY KEY,
  check_date DATE NOT NULL,
  norm_hours FLOAT NOT NULL,
  qaqc_hours FLOAT NOT NULL,
  ot_hours FLOAT NOT NULL,
  gross FLOAT NOT NULL,
  tax FLOAT NOT NULL,
  tax_percent FLOAT NOT NULL,
  post_tax_ded FLOAT NOT NULL,
  net FLOAT NOT NULL
);
CREATE TABLE IF NOT EXISTS necessities (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  expected_cost FLOAT NOT NULL,
  exp_yearly_cost FLOAT NOT NULL,
  exp_percent_net FLOAT NOT NULL
);
CREATE TABLE IF NOT EXISTS bills (
  bill_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  due_date DATE NOT NULL,
  cost FLOAT NOT NULL,
  yearly_cost FLOAT NOT NULL,
  percent_net FLOAT NOT NULL
);
CREATE TABLE IF NOT EXISTS loans(
  loan_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  due_date DATE NOT NULL,
  cost FLOAT NOT NULL,
  yearly_cost FLOAT NOT NULL,
  percent_net FLOAT NOT NULL
);
