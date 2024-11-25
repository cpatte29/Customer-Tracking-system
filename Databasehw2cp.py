import sqlite3
import datetime

# SQL Queries
CREATE_CUSTOMERS_TABLE = """CREATE TABLE IF NOT EXISTS customers
    (customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    customer_number TEXT);"""

CREATE_LOCATIONS_TABLE = """CREATE TABLE IF NOT EXISTS locations
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    address TEXT,
    city TEXT,
    state TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id));"""

CREATE_SERVICES_TABLE = """CREATE TABLE IF NOT EXISTS services
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT,
    cost REAL);"""

CREATE_EQUIPMENT_TABLE = """CREATE TABLE IF NOT EXISTS equipment
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    equip_name TEXT,
    cost REAL);"""

CREATE_CUSTOMER_SERVICE_TABLE = """CREATE TABLE IF NOT EXISTS customer_services
    (customer_id INTEGER,
    location_id INTEGER,
    service_id INTEGER,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(location_id) REFERENCES locations(id),
    FOREIGN KEY(service_id) REFERENCES services(id));"""

CREATE_CUSTOMER_EQUIPMENT_TABLE = """CREATE TABLE IF NOT EXISTS customer_equipment
    (location_id INTEGER,
    equipment_id INTEGER,
    FOREIGN KEY(location_id) REFERENCES locations(id),
    FOREIGN KEY(equipment_id) REFERENCES equipment(id));"""

CREATE_BILLING_TABLE = """CREATE TABLE IF NOT EXISTS billing
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    due_date REAL,
    last_payment_date TEXT,
    is_late INTEGER,
    amount_due TEXT,
    credit_card_number TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id));"""

INSERT_CUSTOMER = "INSERT INTO customers (name, customer_number) VALUES (?, ?)"
INSERT_LOCATION = "INSERT INTO locations (customer_id, address, city, state) VALUES (?, ?, ?, ?);"
INSERT_SERVICE = "INSERT INTO services (service_name, cost) VALUES (?, ?);"
INSERT_EQUIPMENT = "INSERT INTO equipment (equip_name, cost) VALUES (?, ?);"
INSERT_CUSTOMER_SERVICE = "INSERT INTO customer_services (customer_id, location_id, service_id) VALUES (?, ?, ?);"
INSERT_CUSTOMER_EQUIPMENT = "INSERT INTO customer_equipment (location_id, equipment_id) VALUES (?, ?);"
INSERT_BILLING = "INSERT INTO billing (customer_id, amount_due, last_payment_date, is_late, due_date, credit_card_number) VALUES (?, ?, ?, ?, ?);"

SELECT_ALL_CUSTOMERS = "SELECT * FROM customers;"
SELECT_CUSTOMER_BY_NAME = "SELECT * FROM customers WHERE name LIKE ?;"
SELECT_CUSTOMER_BY_LOCATION = "SELECT customers.* FROM customers JOIN locations ON customers.id = locations.customer_id WHERE locations.address LIKE ?;"
SELECT_LATE_PAYMENTS = "SELECT * FROM billing WHERE is_late = 1;"

CHECK_CUSTOMER_EXISTS = "SELECT * FROM customers WHERE name LIKE ?;"
CHECK_LOCATION_EXISTS = "SELECT * FROM locations WHERE address LIKE ?;"

DELETE_CUSTOMER_BY_ID = """DELETE FROM customers WHERE name LIKE ?;"""
DELETE_CUSTOMER_SERVICE = """DELETE FROM customer_services WHERE customer_id = ? AND location_id = ? AND serivce_id = ?;"""

connection = sqlite3.connect("customer_tracking.db")

# making a payment to add into billing / not in directions
def make_payment(customer_id, amount_paid, credit_card_number):
    payment_date = datetime.now().strftime("%Y-%m-%d")
    with connection:
        cursor = connection.cursor()

        # Get the current amount due for the customer from the billing table
        cursor.execute("SELECT amount_due FROM billing WHERE customer_id = ?", (customer_id,))
        billing_info = cursor.fetchone()

        if billing_info:
            current_amount_due = billing_info[0]

            # Ensure the payment doesn't exceed the current amount due
            if amount_paid > current_amount_due:
                print("Payment exceeds the amount due.")
                return

            # Update the billing table: reduce the amount due and set the last payment date
            cursor.execute("""
                UPDATE billing
                SET amount_due = amount_due - ?, last_payment_date = ?, credit_card_number = ?
                WHERE customer_id = ?
            """, (amount_paid, payment_date, credit_card_number, customer_id))

            connection.commit()
            print("Payment recorded successfully.")
        else:
            print("No billing information found for this customer.")



def create_tables():
    with connection:
        connection.execute(CREATE_CUSTOMERS_TABLE)
        connection.execute(CREATE_LOCATIONS_TABLE)
        connection.execute(CREATE_SERVICES_TABLE)
        connection.execute(CREATE_EQUIPMENT_TABLE)
        connection.execute(CREATE_CUSTOMER_SERVICE_TABLE)
        connection.execute(CREATE_CUSTOMER_EQUIPMENT_TABLE)
        connection.execute(CREATE_BILLING_TABLE)

# adding a customer
def add_customer(name, customer_number):
    with connection:
        cursor = connection.cursor()
        cursor.execute(INSERT_CUSTOMER, (name, customer_number))
    return cursor.lastrowid

# adding location
def add_location(customer_id, address, city, state):
    with connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO locations (customer_id, address, city, state) VALUES (?, ?, ?, ?)",
                       (customer_id, address, city, state))
    return cursor.lastrowid

# Searching all locations
def get_locations_for_customer(customer_id):
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, address FROM locations WHERE customer_id = ?", (customer_id,))
        return cursor.fetchall()  # Return all locations for the customer as (id, address) tuples


def remove_customer(column: str, value):
    with connection:
        cursor = connection.cursor()
        query = f"DELETE FROM customers WHERE {column} = ?"
        cursor.execute(query, (value,))
    return cursor.rowcount  # Returns the number of rows deleted

# get every customer
def get_all_customers():
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT customer_id, name FROM customers")
        return cursor.fetchall()  # Return all customers as (id, name) tuples


# for searching customer by location name or id
def search_customers_by_name(name):
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT customer_id, name, customer_number FROM customers WHERE name LIKE ?", ('%' + name + '%',))
        return cursor.fetchall()  # Return all matching customers

def search_customer_by_id(customer_id):
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        return cursor.fetchall()  # Return customer with the specified ID

def search_customers_by_location(address):
    with connection:
        cursor = connection.cursor()
        cursor.execute(SELECT_CUSTOMER_BY_LOCATION, ('%' + address + '%',))  # Use LIKE for partial matching
        return cursor.fetchall()  # Return customers at the specified location


#Late payment section

def is_payment_late(last_payment_date_str):
    # Convert the last payment date string from the database into a datetime object
    date_object = datetime.datetime.strptime(last_payment_date_str, "%Y-%m-%d")

    thirty_days_in_seconds = datetime.timedelta(days=30).total_seconds()
    todays_timestamp = datetime.datetime.today().timestamp()
    timestamp_of_last_payment = date_object.timestamp()

    # Check if the payment is late based on days
    if todays_timestamp - timestamp_of_last_payment >= thirty_days_in_seconds:
        return True

#  check if payment is late
def get_late_payments():
    """Retrieve all late payments."""
    today = datetime.date.today()  # Get today's date
    with connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT b.id, c.name, b.due_date, b.last_payment_date
            FROM billing b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.due_date < ?
        """, (today,))

        late_payments = []
        for payment in cursor.fetchall():
            payment_id, customer_name, due_date, last_payment_date = payment

            # Checks if the payment is late
            if is_payment_late(last_payment_date):
                late_payments.append((payment_id, customer_name, due_date))

        return late_payments  # Return all late payment records

# service & equipment
def add_service(service_name, cost):
    with connection:
        cursor = connection.cursor()
        cursor.execute(INSERT_SERVICE, (service_name, cost))

def add_customer_service(customer_id, location_id, service_id):
    with connection:
        cursor = connection.cursor()
        cursor.execute(INSERT_CUSTOMER_SERVICE, (customer_id, location_id, service_id))
        return cursor.lastrowid


def remove_customer_service(customer_id,location_id, service_id):
    with connection:
        cursor = connection.cursor()
        cursor.execute(DELETE_CUSTOMER_SERVICE, (customer_id, location_id ,service_id))
        return cursor.rowcount

# dict for rates
fixed_service_rates = {
    "Internet": 50.00,
    "Cable": 70.00,
    "Phone": 30.00,}

def get_fixed_service_cost(service_name):
    return fixed_service_rates.get(service_name)

def update_service_cost(service_id, new_cost):
    with connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE services SET cost = ? WHERE id = ?", (new_cost, service_id))
    return cursor.rowcount  # Returns the number of rows updated

def update_equipment_cost(equipment_id, new_cost):
    with connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE equipment SET cost = ? WHERE id = ?",
                       (new_cost, equipment_id))
    return cursor.rowcount  # Returns the number of rows updated

# billing
def get_billing_info(customer_id):
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT customer_id, amount_due, due_date, last_payment_date FROM billing WHERE customer_id = ? ",
                       (customer_id,))
        return cursor.fetchone()  # Return the first matching billing record

def update_last_payment_date(customer_id, new_payment_date):
    with connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE billing SET last_payment_date = ? WHERE customer_id = ?", (new_payment_date, customer_id))
    return cursor.rowcount  # Returns the number of rows updated


def update_billing(customer_id, amount_paid):
    with connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE billing
            SET amount_due = amount_due - ?
            WHERE customer_id = ?
        """, (amount_paid, customer_id))
        connection.commit()

def add_billing(customer_id, due_date, amount_due, last_payment_date, is_late, credit_card_number):
    with connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO billing (customer_id, due_date, amount_due, last_payment_date, is_late, credit_card_number)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (customer_id, due_date, amount_due, last_payment_date, is_late, credit_card_number))
        return cursor.lastrowid
