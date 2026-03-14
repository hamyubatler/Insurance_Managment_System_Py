"""Module for handling insurance policy selection and viewing."""
import re

# pylint: disable=global-statement
CUSTOMER_ID_GLOBAL = 0

HEALTH_INSURANCES = [
    {"policy_name": "HDFC Ergo Health Insurance",
     "sum_assured": 5000000, "premium": 9000, "term": 1},
    {"policy_name": "Max Bupa Health Insurance",
     "sum_assured": 10000000, "premium": 12000, "term": 1},
    {"policy_name": "Star Health Insurance",
     "sum_assured": 8000000, "premium": 10500, "term": 1}
]

MOTOR_INSURANCES = [
    {"policy_name": "Third-Party Liability",
     "sum_assured": 10000, "premium": 500, "term": 1},
    {"policy_name": "Comprehensive Insurance",
     "sum_assured": 20000, "premium": 1000, "term": 2},
    {"policy_name": "Motorcycle Insurance",
     "sum_assured": 5000, "premium": 250, "term": 1}
]

GENERAL_INSURANCES = [
    {"policy_name": "Bajaj Allianz General",
     "sum_assured": 500000, "premium": 7000, "term": 1},
    {"policy_name": "TATA AIG General",
     "sum_assured": 800000, "premium": 8000, "term": 1},
    {"policy_name": "ICICI Lombard General",
     "sum_assured": 700000, "premium": 7500, "term": 1}
]


def policy_page(customer_id):
    """Displays the main policy selection page for a customer."""
    # pylint: disable=import-outside-toplevel
    import Methods

    global CUSTOMER_ID_GLOBAL
    CUSTOMER_ID_GLOBAL = customer_id
    print(f"\nWelcome, Your Customer Id : {customer_id}")

    log = input("1. View Details\n2. Select Policy\n3. Main Menu\n\nOption No : ")

    while not re.match(r'^[1-3]$', log):
        print("Invalid Option! Select from the below option\n")
        log = input("1. View Policies\n2. Select Policy\n3. Main Menu\n\nOption No : ")

    if log == '1':
        Methods.display_customer(customer_id)
        policy_page(CUSTOMER_ID_GLOBAL)
    elif log == '2':
        print("\nInsurance Policy Selection")
        info_1 = input("1. Health\n2. Motor\n3. General\n4. Main Menu\n\nOption No : ")
        while not re.match(r'^[1-4]$', info_1):
            print("Invalid Option! Select from the below option\n")
            info_1 = input("1. Health\n2. Motor\n3. General\n4. Go Back\n\nOption No : ")
        python_switch_2(int(info_1))
    else:
        print()
        Methods.login_input()


def python_switch_2(argument):
    """Switch case for selecting the type of insurance."""
    if argument == 1:
        select_policy(HEALTH_INSURANCES)
    elif argument == 2:
        select_policy(MOTOR_INSURANCES)
    elif argument == 3:
        select_policy(GENERAL_INSURANCES)
    else:
        policy_page(CUSTOMER_ID_GLOBAL)


def select_policy(root_insurances):
    """Allows the user to select a policy from the available options."""
    # pylint: disable=import-outside-toplevel
    import Methods

    i = 1
    for ins in root_insurances:
        i_name = ins["policy_name"]
        s_assure = ins["sum_assured"]
        prem = ins["premium"]
        term = ins["term"]
        print(f"{i}. {i_name} - Sum: {s_assure}, Prem: {prem}, Term: {term} yr")
        i += 1

    option = input("\nSelect one policy : ")
    while not re.match(r'^[1-3]$', option):
        option = input("Invalid Option! Select valid option\nSelect one policy : ")
    option = int(option) - 1

    prompt = f"\nSelected:\n{root_insurances[option]}\n\nPress y to Confirm: "
    if input(prompt) == 'y':
        policy_id = Methods.generate_secure_id()
        Methods.insert_policy_info(
            CUSTOMER_ID_GLOBAL, policy_id, root_insurances[option]["policy_name"],
            root_insurances[option]["sum_assured"], root_insurances[option]["premium"],
            root_insurances[option]["term"]
        )
        policy_page(CUSTOMER_ID_GLOBAL)