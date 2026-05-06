"""Module containing the core business logic and database operations."""
# pylint: disable=invalid-name, too-many-arguments, too-many-locals, too-many-lines, too-many-positional-arguments
import os
import secrets
import re
import mysql.connector
from mysql.connector import Error
from prettytable import PrettyTable
import bcrypt
from dotenv import load_dotenv

load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")
AGENT_PASSWORD = os.getenv("AGENT_PASSWORD")
PEPPER = os.getenv("SECRET_PEPPER")

def login_input():
    """Displays the initial login menu."""
    print("Home Page\n")
    menu = "1. Customer Registration\n2. Login\n3. Agent Login\n4. Exit\nOption: "
    info_1 = input(menu)
    while not re.match(r'^[1-4]$', info_1):
        print("Invalid Option! Select from the below option\n")
        info_1 = input(menu)
    python_switch_1(int(info_1))


def python_switch_1(argument):
    """Switch case for the login page."""
    if argument == 1:
        customer_registration()
    elif argument == 2:
        customer_login()
    elif argument == 3:
        agent_login()
    else:
        print("Welcome Back!")


def back_but():
    """Returns the user to the main menu."""
    input("\nPress Enter key to go back to main menu\n")
    login_input()


def generate_secure_id(length=7):
    """Generates a cryptographically secure numeric ID."""
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def customer_registration():
    """Handles new customer registration and validation."""
    customer_id = generate_secure_id()
    print("\nRegistration Page")

    name = input("Enter Full Name   : ")
    while not re.match(r'^[a-zA-Z ]{2,50}$', name):
        name = input("Invalid Name! Enter Full Name : ")

    age = input("Enter Age         : ")
    while not re.match(r'^(1[8-9]|[2-9][0-9]|1[0-2][0-9]|130)$', age):
        age = input("Invalid Age! Enter Age (18-130): ")

    gender = input("Enter Gender      : ")
    while not re.match(r'^(male|female|Others)$', gender):
        gender = input("Invalid Gender! Enter Gender : ")

    contact = input("Enter Contact No  : ")
    while not re.match(r'^\d{10}$', contact):
        contact = input("Invalid No! Enter 10 digit No: ")

    email = input("Enter Email Id    : ")
    while not re.match(r'^[a-z\d]+@[a-z]{2,30}\.com$', email):
        email = input("Invalid Email! Enter Email Id: ")

    pwd = input("Enter Password    : ")
    while not re.match(r'^[a-zA-Z\W\d]{8,30}$', pwd):
        pwd = input("Invalid! Enter Password (8-30 chars, special, num): ")

    address = input("Enter Address     : ")
    while not re.match(r'^[a-zA-Z\d\W]{5,150}$', address):
        address = input("Invalid Address! Enter Address: ")

    n_name = input("Enter Nominee Name: ")
    while not re.match(r'^[a-zA-Z ]{2,50}$', n_name):
        n_name = input("Invalid Nominee! Enter Name  : ")

    n_rel = input("Enter Relationship: ")
    while not re.match(r'^[a-zA-Z ]{2,80}$', n_rel):
        n_rel = input("Invalid! Enter Relationship  : ")

    if check_customer(contact, email):
        insert_customer(customer_id, name, age, gender, contact,
                        email, pwd, address, n_name, n_rel)
    else:
        print("Customer with same Phone number or emailId is already Present\n")
    back_but()


def customer_login():
    """Handles customer login."""
    print("\nLogin Page")
    customer_id = input("Customer Id   : ")
    pass_word = input("Password      : ")
    login_check(customer_id, pass_word)


def agent_login():
    """Handles agent login."""
    print("\nAgent Login Page")
    input("Agent Id      : ")
    pass_word = input("Password      : ")
    if pass_word == AGENT_PASSWORD:
        agent_view()
    else:
        print("Incorrect Password...")
    back_but()


def agent_view():
    """Retrieves and displays all customers and policies for agents."""
    conn = create_db_connection("localhost", "root", DB_PASSWORD, "mysql_python")
    if not conn:
        return
    # SQL Query broken down to prevent C0301 Line Too Long error
    sql = """SELECT c.Customer_id, c.Customer_Name, c.Contact_Number, 
             c.Email_Id, c.Address, p.Policy_id, p.Policy_Name, 
             p.Sum_Assured, p.Premium, p.Term 
             FROM customer_info as c INNER JOIN policy_info as p 
             ON c.Customer_id = p.Customer_id"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        agent_table(result)
    except Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()


def create_db_connection(host_name, user_name, user_password, db_name=None):
    """Creates a secure connection to the MySQL server."""
    connection = None
    try:
        if db_name:
            connection = mysql.connector.connect(
                host=host_name, user=user_name, password=user_password, database=db_name
            )
        else:
            connection = mysql.connector.connect(
                host=host_name, user=user_name, password=user_password
            )
    except Error:
        print("A secure connection could not be established. Please try again later.")
    return connection


def execute_query(connection, query):
    """Executes a given SQL query."""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err:
        print(f"Error: {err}")


def server():
    """Initializes Server and Tables using consolidated connection logic."""
    conn = create_db_connection("localhost", "root", DB_PASSWORD)
    if conn:
        execute_query(conn, "CREATE DATABASE IF NOT EXISTS mysql_python")
        conn.close()

    conn = create_db_connection("localhost", "root", DB_PASSWORD, "mysql_python")
    if conn:
        create_table(conn)
        conn.close()


def create_table(connection):
    """Creates the necessary database tables."""
    query_c = """CREATE TABLE IF NOT EXISTS customer_info (
      Customer_id VARCHAR(255) PRIMARY KEY,
      Customer_Name VARCHAR(255) NOT NULL,
      Customer_Age INT NOT NULL,
      Customer_Gender ENUM('Male', 'Female', 'Others') NOT NULL,
      Contact_Number VARCHAR(20) NOT NULL,
      Email_Id VARCHAR(255) NOT NULL,
      Password VARCHAR(255) NOT NULL,
      Address TEXT NOT NULL,
      Nominee_Name VARCHAR(255) NOT NULL,
      Nominee_relationship VARCHAR(255) NOT NULL
    );"""
    execute_query(connection, query_c)

    query_p = """CREATE TABLE IF NOT EXISTS policy_info (
      Customer_id VARCHAR(255),
      Policy_id VARCHAR(255),
      Policy_Name VARCHAR(255) NOT NULL,
      Sum_Assured INT NOT NULL,
      Premium VARCHAR(20) NOT NULL,
      Term VARCHAR(255) NOT NULL,
      FOREIGN KEY (Customer_id) REFERENCES customer_info(Customer_id)
    );"""
    execute_query(connection, query_p)


def check_customer(contact_number, email_id):
    """Checks if a customer already exists in the database."""
    conn = create_db_connection("localhost", "root", DB_PASSWORD, "mysql_python")
    if not conn:
        return False
    sql = "SELECT * FROM customer_info WHERE Contact_Number = %s OR Email_Id = %s"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (contact_number, email_id))
        result = cursor.fetchall()
        return not bool(result)
    except Error as err:
        print(f"Error: {err}")
        return False
    finally:
        conn.close()


def insert_customer(cust_id, name, age, gender, contact, email, pwd, add, n_name, n_rel):
    """Inserts a new customer record with a hashed password."""
    conn = create_db_connection("localhost", "root", DB_PASSWORD, "mysql_python")
    if not conn:
        return
    peppered_password = pwd + PEPPER
    hashed = bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt())

    sql = """INSERT INTO customer_info (Customer_id, Customer_Name, Customer_Age, 
             Customer_Gender, Contact_Number, Email_Id, Password, Address, 
             Nominee_Name, Nominee_relationship) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    val = (cust_id, name, age, gender, contact, email, hashed, add, n_name, n_rel)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, val)
        conn.commit()
        print(f"Customer Registered Successfully. ID: {cust_id}")
    except Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()


def login_check(customer_id, pass_word):
    """Validates customer login against hashed database passwords."""
    # pylint: disable=import-outside-toplevel
    import policy

    conn = create_db_connection("localhost", "root", DB_PASSWORD, "mysql_python")
    if not conn:
        return
    sql = "SELECT * FROM customer_info WHERE Customer_id = %s"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (customer_id,))
        result = cursor.fetchall()
        if not result:
            print(f"{customer_id} is not registered")
            back_but()
        else:
            stored_hash = result[0][6]
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            peppered_input = pass_word + PEPPER            
            if bcrypt.checkpw(peppered_input.encode('utf-8'), stored_hash):
                policy.policy_page(customer_id)
            else:
                print("Incorrect Password")
                back_but()
    except Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()


def insert_policy_info(customer_id, policy_id, policy_name, sum_assured, premium, term):
    """Inserts purchased policy details into the database."""
    conn = create_db_connection("localhost", "root", DB_PASSWORD, "mysql_python")
    if not conn:
        return
    sql = """INSERT INTO policy_info (Customer_id, Policy_id, Policy_Name, 
             Sum_Assured, Premium, Term) VALUES (%s, %s, %s, %s, %s, %s)"""
    val = (customer_id, policy_id, policy_name, sum_assured, premium, term)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, val)
        conn.commit()
        print(f"Policy Taken Successfully. ID: {policy_id}")
    except Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()


def display_customer(customer_id):
    """Retrieves and displays specific customer and policy records."""
    conn = create_db_connection("localhost", "root", DB_PASSWORD, "mysql_python")
    if not conn:
        return
    sql = """SELECT * FROM customer_info INNER JOIN policy_info 
             ON customer_info.Customer_id = policy_info.Customer_id 
             WHERE customer_info.Customer_id = %s"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (customer_id,))
        result = cursor.fetchall()
        table(result)
        input("\npress Enter Key to Continue...")
    except Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()


def table(value):
    """Formats customer data into a readable CLI table."""
    x_table = PrettyTable()
    x_table.field_names = ["ID", "Name", "Age", "Gender", "Contact", "Email",
                           "Pass", "Add", "Nom_N", "Nom_R", "P_ID", "P_Name",
                           "Sum", "Prem", "Term"]
    for val in value:
        x_table.add_row([
            val[0], val[1], val[2], val[3], val[4], val[5], "HIDDEN",
            val[7], val[8], val[9], val[10], val[12], val[13], val[14], val[15]
        ])
    x_table.align = "l"
    print(x_table)


def agent_table(value):
    """Formats agent view data into a readable CLI table."""
    x_table = PrettyTable()
    x_table.field_names = ["Cust_ID", "Name", "Contact", "Email", "Address",
                           "Pol_ID", "Pol_Name", "Sum", "Prem", "Term"]
    for val in value:
        x_table.add_row([val[0], val[1], val[2], val[3], val[4], val[5],
                         val[6], val[7], val[8], val[9]])
    x_table.align = "l"
    print(x_table)