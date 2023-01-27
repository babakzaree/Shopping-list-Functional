import os
import json
import logging
import logging.config
from enum import Enum
# Shopping list by Bobby zare (Functional Version)

# Configuration logging using Custom TOML config file
logging.config.fileConfig(fname='log_configuration.toml', disable_existing_loggers=False) # noqa E501

# Creating a logger
logger = logging.getLogger()

# database of users for shopping list program.
with open('./json_files/users.json', mode='r') as f:
    users: dict = json.load(f)

# Discount codes database
with open('./json_files/discount_codes.json', mode='r') as f:
    DISCOUNT_CODE_DATABASE: dict = json.load(f)

# Database of products available. iclude price and amount.
with open('./json_files/products.json', mode='r') as f:
    products: dict = json.load(f)


# Commands of program (Using Enum)
class Command(Enum):
    EXIT = ('quit', 'q', 'ex', 'exit')
    PRODUCTS = ('prods', 'products', 'product')
    DELETE = "delete"
    SHOW = "show"
    HELP = "help"
    BUY = 'buy'
    ADDMONEY = "addmoney"
    CATEGORY = ('category', 'categories')
    LOGOUT = 'logout'


# an dictionary that contains in the shopping list
choosen_items = dict()

# order of showing items in cart (only in store mode)
order = 'default'

# Functions Defined Here...


def clear_screen():
    """clear the terminal."""
    return os.system('clear')


def update_user_balance(user_balance: float, username, users_database):
    """
    Update the user's balance in database.

    Parameters
    ----------
    user_balance: float : balance of user

    username : username of user

    users_database : users database


    Returns
    -------

    """
    users_database[username]['balance'] = user_balance
    with open('./json_files/users.json', mode='w') as f:
        json.dump(users_database, f, indent=4)


def update_products(products_database: dict):
    """
    Update the database of products.

    Parameters
    ----------
    products_database: dict : database of products.


    Returns
    -------

    """
    with open('./json_files/products.json', mode='w') as f:
        json.dump(products_database, f, indent=4)


def load_users_database():
    """load / Reload users database."""
    with open('./json_files/users.json', mode='r') as f:
        return json.load(f)


def create_account(username, password, users_database: dict):
    """
    adding new account to users database.

    Parameters
    ----------
    username : given username

    password : given password

    users_database: dict : database of users


    Returns
    -------
    Return False if the username was exist in database; otherwise True.
    """

    if username in users_database:
        return False
    users_database[username] = {
            "password": password,
            "balance": 30000
        }
    with open('./json_files/users.json', mode='w') as f:
        json.dump(users_database, f, indent=3, separators=(', ', ': '))
    return True


def show_cart(cart: dict, showing_order: str = 'default'):
    """Print items in the Online shop cart verticaly. (store mode)

    Parameters
    ----------
    cart: dict : cart is dictionary of items that user added for purchase
    (in store mode)

    showing_order : order of showing items in cart
         (Default value = 'Default')

    Returns
    -------

    """
    showing_order = showing_order.upper()
    if len(cart) > 0:
        print(f"**(Order: {showing_order}) Items in your Cart: \n")
        all_items_price = float()
        index = 0  # indexing the items in shopping list
        for name, amount in cart.items():  # (in choosen_list)
            pure_item_price = product_price(name)
            price = (pure_item_price * amount)  # Price of item
            index += 1  # starts from 1
            name = name.capitalize()
            all_items_price += price
            print(f"{index}. Name: {name} ][ Price: {pure_item_price} tomans ][ amount: {amount} | Total Price: {price}") # noqa E501
        print("\n===========================================================")
        print(f"Total items: {len(cart)} | Total price: {all_items_price}")
    else:
        print("Oops! Your cart is empty.\n")


def show_list(shopping_list: dict):
    """Showing Shopping List (list mode)

    Parameters
    ----------
    shopping_list: dict :
    shopping_list is dictionary of items that user added for purchase
    (in list mode)

    Returns
    -------

    """
    if len(shopping_list) > 0:
        print("** Items in your Cart: \n")
        all_items_price = float()
        index = 0  # indexing the items in shopping list
        for name, information in shopping_list.items():  # (in choosen_list)
            pure_item_price = information[0]
            amount = information[1]
            price = (pure_item_price * amount)  # Price of item
            index += 1  # starts from 1
            name = name.capitalize()
            all_items_price += price
            print(f" {index}. Name: {name} | Price: {pure_item_price} tomans | amount: {amount} | Total Price: {price}") # noqa E501
        print("\n===========================================================") # noqa E501
        print(f"Total items: {len(shopping_list)} | Total price: {all_items_price}") # noqa E501
    else:
        print("Oops! Your cart is empty.")


def products_by_category(category_name, database_of_products: dict) -> dict:
    """
    return the product of given category
    Parameters
    ----------
    category_name : name of category

    database_of_products: dict :
    a database that contains the products of store

    Returns
    -------
    dictionary of products in given category
    """
    result = dict()
    for name, information in database_of_products.items():
        if information['category'] == category_name:
            result[name] = information
    return result


def order_by_amount(shopping_list: dict) -> dict:
    """
    change the order of showing items in shopping list by amount
    Parameters
    ----------
    shopping_list: dict : dictionary of products that user added


    Returns
    -------
    shopping list sorted by amount (increasing)

    """

    values_sorted = sorted(list(shopping_list.values()))

    result = dict()
    for value in values_sorted:
        for name, amount in shopping_list.items():
            if value == amount:
                result[name] = amount
    return result


def order_by_name(shopping_list: dict) -> dict:
    """
    change the order of showing items in shopping list by name
    Parameters
    ----------
    shopping_list: dict : dictionary of products that user added


    Returns
    -------
    shopping list sorted by name (alphabetic)


    """

    keys_sorted = sorted(list(shopping_list.keys()))

    result = dict()
    for key in keys_sorted:
        for name, amount in shopping_list.items():
            if key == name:
                result[name] = amount
    return result


def buy(balance: float, product_name: str, amount: int):
    """
    return user's balance after decreasing the price of product.

    Parameters
    ----------
    balance: float : balance of user

    product_name: str : name of product that user wants to buy

    amount: int : amount of product that user wants to buy

    Returns
    -------
    if the user balance after decraesing is less than zero(
        user havn't enough money) then Return False
    if the decreasing was successful, Return Balance

    """
    price = float()
    price += (product_price(product_name) * amount)
    balance -= price

    if balance < 0:  # if the balance at the end is less than 0
        return False

    return balance


def refund(balance: float, item_price: float, amount: int) -> float:
    """
    refund the money of user

    Parameters
    ----------
    balance: float : balance of user

    item_price: float : price of item

    amount: int : amount of item


    Returns
    -------
    sum of user's balance with price of item * amount of it
    """
    return balance + (item_price * amount)


def show_help():
    """Read and Print the program's help from file"""
    with open('./message_files/help_message.txt', mode='r') as help_file:
        help_message = help_file.read()
    print(help_message)


def add_item(item_name: str, amount: int, shopping_list: dict):
    """Add item and amount of it to shopping list

    Parameters
    ----------
    item_name: str : name of item

    amount: int : amount of item

    shopping_list: dict : list of shopping list


    Returns
    -------
    adding name of item and amount of it to the shopping list.
    (dictionary of shopping list)
    """
    shopping_list[item_name] = amount


def remove_item(item_name: str, shopping_list: dict):
    """remove item from shopping list. Return True if item has been removed.

    Parameters
    ----------
    item_name: str : name of item that user wants to remove

    shopping_list: dict : list of shopping list


    Returns
    -------
    Return True if procces of removing the item was successful.
    """
    increase_stock(shopping_list[item_name], item_name)
    del shopping_list[item_name]
    return True


def product_price(product_name: str):
    """
    Get the price of given product.

    Parameters
    ----------
    product_name: str : name of product


    Returns
    -------
    price of given item


    """
    price = products[product_name]['price']
    return price


def product_amount(product_name: str) -> int:
    """
    amount of given product available in stock

    Parameters
    ----------
    product_name: str : name of product


    Returns
    -------
    return amount of given product available in stock.
    """
    amount = products[product_name]['amount']
    return amount


def increase_stock(amount: int, product_name: str):
    """increase the stock amount

    Parameters
    ----------
    amount: int : given amount for increasing

    product_name: str : name of product


    Returns
    -------
    increase the amount of product in the database.
    """
    products[product_name]['amount'] += amount


def decrease_stock(amount: int, product_name: str):
    """
    decrease the stock amount
    Parameters
    ----------
    amount: int : given amount for decreasing

    product_name: str : name of product


    Returns
    -------
    if the decreasing was successful, Return True


    """
    if (product_amount(product_name) - amount) > 0:
        products[product_name]['amount'] -= amount
        return True


def mode_status() -> str:
    """ """
    return f"\n<{mode.upper()} MODE>"


def is_authenticated(username, password, users_database):
    """
    check if the username and password combination its correct.
    Parameters
    ----------
    username : entered username

    password : entered password

    users_database : database that contains the information of users


    Returns
    -------
    return True if authenication was successful, otherwise False.
    """
    if username in users_database.keys():
        if password == users_database.get(username)['password']:
            return True
    return False


def discount(discount_code, total_price, discount_code_database) -> float:
    """
    calculate the discount of given code.
    Parameters
    ----------
    discount_code : given discount code

    total_price : price that we want to decraese the price of discount from it.

    discount_code_database : database that contains discount codes.

    Returns
    -------
    return the total price after decreasing discount.
    """
    persent_of_discount = discount_code_database[discount_code]
    return (persent_of_discount * total_price) / 100


# Main block of code here

clear_screen()

# Starting message (loaded from ./message_file/help_message.txt)
with open('./message_files/banner.txt', mode='r') as banner_file:
    banner = banner_file.read()
    print(banner)

while True:

    while True:
        print("if you have account, Please login. Or create an account.")
        print("For quit the app, Enter 'quit' .")
        ask_user_to_login = input("Login / Create: ").strip().lower()

        if ask_user_to_login == 'login':
            break

        elif ask_user_to_login == 'create':
            logger.info("User Entered create account state.")
            clear_screen()
            print("Creating new Account...")
            new_username = input("Username: ").strip().lower()
            new_password = input("Password: ").strip().lower()
            if create_account(new_username,
                              new_password,
                              users):
                logger.info(f"An account has been created. USERNAME: {new_username}") # noqa E501
                clear_screen()
                print(f"Your username: {new_username}")
                print(f"Password: {new_password}")
                print("\nPlease do not forget you account's information.")
                users = load_users_database()
                print("\nACCOUNT HAS BEEN CREATED SUCCESSFULLY.")
                break
            else:
                logger.warning(f"Trying to create an taken username: {new_username}") # noqa E501
                clear_screen()
                print("This username is already taken.")

        elif ask_user_to_login in ('q', 'quit', 'ex', 'exit'):
            logger.info("Quited from app in login state.")
            print("Quited.")
            exit()

        else:
            logger.warning(f"Wrong input in login state: {ask_user_to_login}")
            print('WRONG INPUT!')
    # User authenication (Login Feature)

    user_logged_in = False

    while user_logged_in is False:
        logger.info("Entered in login page.")
        print("Login to your Account...")
        # stripped and lowercased version of given username and password
        username = (input("Username: ").strip()).lower()
        logger.info("User trying to login.")
        password = (input("Password: ").strip()).lower()
        # if authenication was successfully
        if is_authenticated(username, password, users):
            clear_screen()
            logger.info(f"User {username} logged in.")
            user_logged_in = True
            print(f'Hello {username}! Welcome back.')
            break
        else:
            logger.warning("Incorrect Username/Pass combination Entered.")
            clear_screen()
            print("username / password combination is incorrect.")
            print("Try again.")

    # Catching user balance from the USERS Database
    user_balance = users.get(username)['balance']
    first_balance = user_balance

    # Choose mode of program
    while True:
        mode = (
            input("Choose mode ('store' / 'list') : ")
                ).strip().lower()
        # Check if user input for mode is correct.
        if mode not in ('store', 'list'):
            logger.warning(f"Wrong input in selecting mode state. Input: {mode}") # noqa E501
            print("Wrong input!")
        else:
            logger.info(f"User {username} Entered '{mode}' mode.")
            clear_screen()
            break

    # While shopping list program is running. <LIST MODE>
    while (mode == 'list') and (user_logged_in is True):
        print(mode_status())
        # striped version of input
        user_input = input("Enter product like this '<name> <price> <amount>': ").strip().lower() # noqa E501
        clear_screen()

        # EXIT command
        if user_input in Command.EXIT.value:
            if choosen_items:  # If choosen_items isn't empty
                print("Your shopping list items:\n")
                show_list(choosen_items)
            break  # Exit the loop

        # DELETE command
        elif (user_input).startswith(Command.DELETE.value):
            while True:
                if len(user_input.split()) < 1:   # checking input format
                    print("Wrong Input!. Check this --> <Delete> <product name> .") # noqa E501
                else:
                    # scrape pure item name from user_input
                    pure_item_name = ((user_input.split())[1])
                    # if item was exist and has been deleted successfully
                    if remove_item(pure_item_name, choosen_items):
                        print(f"""
                        '{pure_item_name}' has been fully deleted successfully.
                        """)
                        show_list(choosen_items)
                        break
                    else:
                        print(f"{pure_item_name} is not in the shopping list.")
                        break

        # HELP command
        elif user_input == Command.HELP.value:
            clear_screen()
            show_help()

        # SHOW items
        elif user_input == Command.SHOW.value:
            show_list(choosen_items)

        # checking user input format for adding item to the shopping list
        elif len(user_input.split()) != 3:
            print(input("WRONG FORMAT! Hit enter to continue..."))

        # add item to shopping list
        else:
            product_name = (user_input.split())[0]
            price = int((user_input.split())[1])
            amount = int((user_input.split())[2])
            if product_name in choosen_items:
                print(f"{amount}  '{product_name}' is already in shopping list.") # noqa E501
            else:
                choosen_items[product_name] = [price, amount]
                print(f"""
                {amount}  '{product_name}' has been added to shopping list.
                """)

    # while the Online shop program is running  <STORE MODE>
    while (mode == 'store') and (user_logged_in is True):
        # Getting input from user
        print(f"({username})", f"$$ {user_balance} tomans", mode_status())
        # striped version of input
        user_input = (input("\nEnter name of product: ").strip()).lower()
        clear_screen()
        logger.info(f"User: {username}| Command: '{user_input}'")
        # EXIT command
        if user_input in Command.EXIT.value:
            if choosen_items:  # If choosen_items isn't empty
                clear_screen()
                print("you'll leave everything unsaved. Are you sure?")
                exit_confirmation = input("Enter <yes> if you want to exit: ")
                if exit_confirmation.strip().lower() == 'yes':
                    print("Hope you come back soon. Have a nice day.")
                    exit()  # Exit the program
                else:
                    print("Canceled.")
            else:
                break

        elif user_input in Command.LOGOUT.value:
            clear_screen()
            user_logout_confirmation = input("Are you sure you want to logout? ").strip().lower() # noqa E501
            if user_logout_confirmation == 'yes':
                clear_screen()
                print("Logglogger out.")
                user_logged_in = False
                logger.info(f"User: {username} Logged out.")
                break

        # AddBalance will add preferred balance to user_balance
        elif user_input in Command.ADDMONEY.value:
            given_balance = int(input("How much money you want to add? Enter: ")) # noqa E501
            while True:
                if given_balance < 0:
                    logger.warning(f"User: {username} wrong input at addbalance: Input: {given_balance}") # noqa E501
                    print("Wrong input! You can't decrease your money!")
                else:
                    logger.info(f"User: {username} Added {given_balance}$ to his/her wallet.") # noqa E501
                    user_balance += given_balance
                    first_balance = user_balance
                    # assining new balance to users database
                    update_user_balance(user_balance, username, users)
                    break

        # PRODUCTS command
        elif user_input in Command.PRODUCTS.value:
            clear_screen()
            print("***** List of our products ***** \n")
            for name, info in products.items():
                print(f"Name: {name.capitalize()} | Price: {info['price']} tomans | {info['amount']} in stock")  # noqa E501
                print("______________________________________________________")
        # Category command: show the products to user by category
        elif user_input in Command.CATEGORY.value:
            clear_screen()
            category = input("Category: ")
            logger.info(f"User: {username} | input:'{given_balance}'")
            for name, info in products_by_category(category, products).items():
                print(f"Name: {name.capitalize()} | Price: {info['price']} tomans | {info['amount']} in stock")  # noqa E501
                print("______________________________________________________")
            logger.info(f"User: {username}| Showing {category} category.")
        # DELETE command
        elif (user_input).startswith(Command.DELETE.value):
            # scrape pure item name from user_input
            pure_item_name = ((user_input.split())[1])
            logger.info(f"User: {username} Trying to delete: {pure_item_name}") # noqa E501
            # Last parameter is the amount of product
            #  that user have in his/her shopping list.
            user_balance = refund(
                user_balance,
                product_price(pure_item_name),
                choosen_items[pure_item_name]
                )
            # if item was exist and has been deleted successfully
            if remove_item(pure_item_name, choosen_items):
                logger.info(f"User: {username} Deleted item: {pure_item_name}") # noqa E501
                print(f"'{pure_item_name}' has been fully deleted successfully.") # noqa E501
            else:
                print(f"{pure_item_name} is not in the shopping list.")
        # ^^^^
        # Order command
        elif len(user_input.split()) > 1:
            if (user_input.split())[0] == 'order':
                logger.info(f"User: {username}: Command: 'order'")
                order = (user_input.split())[1]
                if order == 'amount':
                    print("your list order will be shown by 'amount'.")
                elif order == 'name':
                    print("your list order will be shown by 'name'.")
                elif order == 'default':
                    print("your list order is now on 'default'.")
                else:
                    logger.warning(f"User: {username} |Invalid order type: {order}") # noqa E501
                    print("invalid order.")
                    order = 'default'  # set the order to the default
        # if it was pure Order command:
        elif user_input == 'order':
            clear_screen()
            print("in case of using order command, see the help. enter <help>")

        # SHOW items
        elif user_input == Command.SHOW.value:
            logger.info(f"User: {username} | Showing Cart.")
            # if the order is set to 'amount', show the cart by amount
            if order == 'amount':
                show_cart(order_by_amount(choosen_items), order)
            # if the order is set to 'name', show the cart by name
            elif order == 'name':
                show_cart(order_by_name(choosen_items), order)
            else:
                show_cart(choosen_items, order)

        # HELP command
        elif user_input == Command.HELP.value:
            logger.info(f"User: {username} | Showing help.")
            clear_screen()
            show_help()

        # BUY command
        elif user_input == Command.BUY.value:
            clear_screen()
            if choosen_items:
                # calculating total price of items
                total_price = first_balance - user_balance
                print(f"You are paying {total_price} tomans")
                while True:
                    have_discount_code = input("Do you have Discount code? ")
                    # if user have discount code
                    if have_discount_code.strip().lower() == 'yes':
                        discount_code = input("Enter Discount code: ").strip().lower() # noqa E501
                        logger.info(f"User: {username} Entered discount code:'{discount_code}'") # noqa E501
                        # if the discount code is correct
                        if discount_code in DISCOUNT_CODE_DATABASE:
                            # calculating discount price useing discount() function # noqa E501
                            discount_price = discount(discount_code,
                                                      total_price,
                                                      DISCOUNT_CODE_DATABASE)
                            # if the discount price is more than 300,000 tomans. # noqa E501
                            # set the discount price to 300,000.
                            # because user shouln't have more than 300,000 tomans --> # noqa E501
                            #   --> discount.
                            if discount_price > 300000:
                                discount_price = 300000
                            clear_screen()
                            print(f"You have {DISCOUNT_CODE_DATABASE[discount_code]}% OFF!")    # noqa E501
                            print(f"total price has been decreased {discount_price} tomans.")   # noqa E501
                            print("____________________________")
                            show_cart(choosen_items, order)
                            print("==============================================") # noqa E501
                            print(f"Final price: {total_price - discount_price} | {DISCOUNT_CODE_DATABASE[discount_code]}% OFF") # noqa E501
                            buy_confirmation = input("Enter 'Finish' to buy items (you can 'Cancel' anytime.): ")  # noqa E501
                            if buy_confirmation.strip().lower() == 'finish':
                                logger.info(f"User: {username} Finished the buy.") # noqa E501
                                user_balance += discount_price
                                update_user_balance(user_balance, username, users) # noqa E501
                                update_products(products)
                                user_logged_in = False
                                logger.info(f"User: {username} Has been logged out.") # noqa E501
                                clear_screen()
                                print("Thanks for your Purchase.")
                                break
                            elif buy_confirmation.strip().lower() == 'cancel':
                                logger.info(f"User: {username} Canceled the buy.") # noqa E501
                                break
                        else:
                            print("Incorrect code!")
                    # if user havn't discount code
                    elif have_discount_code.strip().lower() == 'no':
                        logger.info(f"User: {username} Havn't Discount code.")
                        clear_screen()
                        show_cart(choosen_items)
                        buy_confirmation = input("Enter 'Finish' to buy items (you can 'Cancel' anytime.): ")  # noqa E501
                        logger.info(f"User: {username} | input:'{buy_confirmation}'") # noqa E501
                        if buy_confirmation.strip().lower() == 'finish':
                            logger.info(f"User: {username} Finished the buy.")
                            update_products(products)
                            update_user_balance(user_balance, username, users)
                            clear_screen()
                            print("Thanks for your Purchase.")
                            user_logged_in = False
                            break
                        elif buy_confirmation.strip().lower() == 'cancel':
                            logger.info(f"User: {username} Canceled the buy.")
                            print("Canceled.")
                            break
                    else:
                        logger.warning(f"User: {username}| Invalid input: {have_discount_code}") # noqa E501
                        print("ERROR! Invalid input.")
            else:
                print("Your shopping Cart is empty.")
        # procces of adding or removing product
        else:
            # if user input is in Products keys (name of the products)
            if user_input in products.keys():
                logger.info(f"User: {username} Selected 'item:{user_input}'")
                preferred_amount = int(input(f"Enter the amount of '{user_input}'s that you want: ")) # noqa E501
                logger.info(f"User: {username} Selected 'amount':{preferred_amount}") # noqa E501
                # if user have enough money
                if buy(user_balance, user_input, preferred_amount):
                    # if decreasing from store finished correctly
                    if decrease_stock(preferred_amount, user_input):
                        user_balance = buy(
                            user_balance,
                            user_input,
                            preferred_amount
                            )
                        add_item(user_input, preferred_amount, choosen_items)
                        logger.info(f"User: {username} Added {preferred_amount} {user_input} to the cart.") # noqa E501
                        clear_screen()
                        print(f"{preferred_amount} '{user_input}' Has been added successfully.") # noqa E501
                        print("Has been added successfully.")
                    else:
                        print(f"""
                    Sorry!
                    We don't have {preferred_amount} of {user_input} in stock.
                        """)
                else:
                    print(f"""
                You havn't enough money for {preferred_amount} {user_input}'s.
                * You can use 'addmoney' command for increasing your balance.
                    """)
            else:
                print(
                    f"""'{user_input}' is not available in store.
                    check products by 'products' command.""")
