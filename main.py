import os
from datetime import datetime
import mysql.connector

# Database setup
try:
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="admin"
    )

    c = mydb.cursor()

    # Create the database if it doesn't exist
    c.execute("CREATE DATABASE IF NOT EXISTS datable")
    c.execute("USE datable")

    # Create the tables if they don't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS department (
        Department_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
        Department_Name VARCHAR(255) NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS user (
        ID BIGINT PRIMARY KEY AUTO_INCREMENT,
        password VARCHAR(255) NOT NULL,
        User_Name VARCHAR(255) NOT NULL,
        Department_ID BIGINT NOT NULL,
        Access_Level SMALLINT NOT NULL,
        Admin_ID BIGINT,
        FOREIGN KEY (Department_ID) REFERENCES department (Department_ID),
        FOREIGN KEY (Admin_ID) REFERENCES user (ID)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS item (
        Item_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
        Item_Name VARCHAR(255) NOT NULL,
        Department_ID BIGINT NOT NULL,
        Admin_ID BIGINT,
        FOREIGN KEY (Department_ID) REFERENCES department (Department_ID),
        FOREIGN KEY (Admin_ID) REFERENCES user (ID)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS log (
        Log_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
        Item_ID BIGINT NOT NULL,
        User_ID BIGINT NOT NULL,
        Department_ID BIGINT NOT NULL,
        Log_Borrow_Date TIMESTAMP NOT NULL,
        Log_Return_Date TIMESTAMP,
        Log_Status SMALLINT NOT NULL DEFAULT 0,
        FOREIGN KEY (Item_ID) REFERENCES item (Item_ID),
        FOREIGN KEY (User_ID) REFERENCES user (ID),
        FOREIGN KEY (Department_ID) REFERENCES department (Department_ID)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS category (
        Category_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
        Category_Name VARCHAR(255) NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS item_category (
        Item_ID BIGINT NOT NULL,
        Category_ID BIGINT NOT NULL,
        FOREIGN KEY (Item_ID) REFERENCES item (Item_ID),
        FOREIGN KEY (Category_ID) REFERENCES category (Category_ID)
    )
    """)

    print("Database and tables created successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Clear screen function (for a clean interface)
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen for Windows/Linux

# Command-line interface
def cli():
    global mydb, c  # Declare mydb and c as global
    clear_screen()

    # Print logo and scrolling message (using ANSI escape codes)
    print("\033[1;33;40m"  # Set theme (yellow text, black background)
          "✦ Datable\n"
          "\033[0;37;40m"  # Reset text color to white
          "Datable is a next generation AI database built for Data base.\n"
          "Datable is an experimental initiative aimed at bringing your entire workflow to work with ai.\n"
          "\033[1;33;40m"  # Set theme again
          "-------------------------------------------------------------------------\n"
          "\033[0m")       # Reset all formatting

    # Improved menu display with borders
    print("╔════════════════════════════════════════╗")
    print("║                Main Menu                ║")
    print("╠════════════════════════════════════════╣")
    print("║ 1. Display SQL Table                   ║")
    print("║ 2. Manage Item Borrow/Return            ║")
    print("║ 3. Execute Custom SQL Command          ║")
    print("║ 4. Switch to AI Assistant Mode (Dev)    ║")
    print("║ 5. Personnel Management (Dev)          ║")
    print("║ \033[1;31;40m6. Exit\033[0m                         ║")
    print("╚════════════════════════════════════════╝")

    choice = input("Enter your choice: ")

    if choice == '1':
        display_sql_table()
    elif choice == '2':
        manage_item_borrow_return()
    elif choice == '3':
        execute_custom_sql()
    elif choice == '4':
        ai_assistant_mode()
    elif choice == '5':
        personnel_management()
    elif choice == '6':
        mydb.close()  # Close the database connection before exiting
        return
    else:
        print("Invalid choice. Please try again.")

    input("Press Enter to continue...")  # Add a pause before returning to the main menu

# Functionality implementations
def display_sql_table():
    global c  # Use the global c cursor
    table_name = input("Enter the table name to display: ")
    try:
        c.execute(f"SELECT * FROM {table_name}")
        rows = c.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print(f"Table '{table_name}' is empty.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def manage_item_borrow_return():
    global mydb, c  # Use the global mydb and c
    # Example implementation for managing item borrow/return
    action = input("Enter 'borrow' to borrow an item or 'return' to return an item: ")
    if action == 'borrow':
        user_id = input("Enter your user ID: ")
        item_id = input("Enter the item ID to borrow: ")
        department_id = input("Enter your department ID: ")
        borrow_date = datetime.now()
        try:
            c.execute('''INSERT INTO log (Item_ID, User_ID, Department_ID, Log_Borrow_Date, Log_Status)
                         VALUES (?, ?, ?, ?, 0)''', (item_id, user_id, department_id, borrow_date))
            mydb.commit()
            print("Item borrowed successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    elif action == 'return':
        log_id = input("Enter the log ID of the item to return: ")
        return_date = datetime.now()
        try:
            c.execute('''UPDATE log SET Log_Return_Date = ?, Log_Status = 1
                         WHERE Log_ID = ?''', (return_date, log_id))
            mydb.commit()
            print("Item returned successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    else:
        print("Invalid action. Please try again.")

def execute_custom_sql():
    global mydb, c  # Use the global mydb and c
    command = input("Enter your SQL command: ")
    try:
        c.execute(command)
        mydb.commit()
        rows = c.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print("Command executed successfully (no results returned).")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# AI Assistant Mode
def ai_assistant_mode():
    import getpass
    import os
    import langchain
    import langchain_google_genai

    os.environ["GOOGLE_API_KEY"] = 'AIzaSyA7mO8b51xqWmDyH0ijZETCxDdWv-xkAuI'  # Replace with your actual API key

    from langchain.sql_database import SQLDatabase
    from langchain_experimental.sql import SQLDatabaseChain

    # Use your actual MySQL database connection details here
    db = SQLDatabase.from_uri("mysql://root:admin@127.0.0.1:3306/datable")

    from langchain.chains import create_sql_query_chain
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

    from langchain.prompts import PromptTemplate
    import mysql.connector

    explain_prompt_template: str = """
You are an expert data analyst called 'Datable'. Explain and analyze the sql query results. Use the following format:
'''
SQL Result : {sql_result}
Answer: What you want to explain to the User
'''

Tables schema:

CREATE TABLE department (
    Department_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Department_Name VARCHAR(255) NOT NULL
);


CREATE TABLE user (
    ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(255) NOT NULL,
    User_Name VARCHAR(255) NOT NULL,
    Department_ID BIGINT NOT NULL,
    Access_Level SMALLINT NOT NULL,
    FOREIGN KEY (Department_ID) REFERENCES department (Department_ID)
);


ALTER TABLE user
ADD COLUMN Admin_ID BIGINT;


ALTER TABLE user
ADD FOREIGN KEY (Admin_ID) REFERENCES user (ID);


CREATE TABLE item (
    Item_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Item_Name VARCHAR(255) NOT NULL,
    Department_ID BIGINT NOT NULL,
    Admin_ID BIGINT,
    FOREIGN KEY (Department_ID) REFERENCES department (Department_ID),
    FOREIGN KEY (Admin_ID) REFERENCES user (ID)
);


CREATE TABLE log (
    Log_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Item_ID BIGINT NOT NULL,
    User_ID BIGINT NOT NULL,
    Department_ID BIGINT NOT NULL,
    Log_Borrow_Date TIMESTAMP NOT NULL,
    Log_Return_Date TIMESTAMP,
    Log_Status SMALLINT NOT NULL DEFAULT 0,
    FOREIGN KEY (Item_ID) REFERENCES item (Item_ID),
    FOREIGN KEY (User_ID) REFERENCES user (ID),
    FOREIGN KEY (Department_ID) REFERENCES department (Department_ID)
);


CREATE TABLE category (
    Category_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Category_Name VARCHAR(255) NOT NULL
);


CREATE TABLE item_category (
    Item_ID BIGINT NOT NULL,
    Category_ID BIGINT NOT NULL,
    FOREIGN KEY (Item_ID) REFERENCES item (Item_ID),
    FOREIGN KEY (Category_ID) REFERENCES category (Category_ID)
);
"""

    prompt_template: str = """
You are an expert data analyst called 'Datable'. Given an input question: {user_question}. First create a syntactically correct query to run, tell the user. Use the following format:
'''
Use_SQL: Y or N
SQLQuery: SQL Query to run
Answer: What you want to tell the User
'''

Only use the following tables schema:

CREATE TABLE department (
    Department_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Department_Name VARCHAR(255) NOT NULL
);


CREATE TABLE user (
    ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(255) NOT NULL,
    User_Name VARCHAR(255) NOT NULL,
    Department_ID BIGINT NOT NULL,
    Access_Level SMALLINT NOT NULL,
    FOREIGN KEY (Department_ID) REFERENCES department (Department_ID)
);


ALTER TABLE user
ADD COLUMN Admin_ID BIGINT;


ALTER TABLE user
ADD FOREIGN KEY (Admin_ID) REFERENCES user (ID);


CREATE TABLE item (
    Item_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Item_Name VARCHAR(255) NOT NULL,
    Department_ID BIGINT NOT NULL,
    Admin_ID BIGINT,
    FOREIGN KEY (Department_ID) REFERENCES department (Department_ID),
    FOREIGN KEY (Admin_ID) REFERENCES user (ID)
);


CREATE TABLE log (
    Log_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Item_ID BIGINT NOT NULL,
    User_ID BIGINT NOT NULL,
    Department_ID BIGINT NOT NULL,
    Log_Borrow_Date TIMESTAMP NOT NULL,
    Log_Return_Date TIMESTAMP,
    Log_Status SMALLINT NOT NULL DEFAULT 0,
    FOREIGN KEY (Item_ID) REFERENCES item (Item_ID),
    FOREIGN KEY (User_ID) REFERENCES user (ID),
    FOREIGN KEY (Department_ID) REFERENCES department (Department_ID)
);


CREATE TABLE category (
    Category_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Category_Name VARCHAR(255) NOT NULL
);


CREATE TABLE item_category (
    Item_ID BIGINT NOT NULL,
    Category_ID BIGINT NOT NULL,
    FOREIGN KEY (Item_ID) REFERENCES item (Item_ID),
    FOREIGN KEY (Category_ID) REFERENCES category (Category_ID)
);
"""
    explain_prompt = PromptTemplate.from_template(template=explain_prompt_template)
    prompt = PromptTemplate.from_template(template=prompt_template)

    global sql_query  # Declare sql_query as global

    user_question = input("Type your question: ")
    print("====================================")

    prompt_formatted_str: str = prompt.format(user_question=user_question)
    prediction = llm.predict(prompt_formatted_str)

    sections = prediction.split("'''")
    use_SQL = sections[1].strip().split('\n')[0].split(': ')[1]
    SQLQuery = sections[2].strip().split('\n')[0].split(': ')[1]
    Answer = sections[3].strip().split('\n')[0].split(': ')[1]

    if use_SQL.upper() == "N":
        bot_message = Answer
        print(bot_message)
    elif use_SQL.upper() == "Y":
        sql_query = SQLQuery  # Assign a value to sql_query
        print(f"""
==================================================================

Do you want to run this SQL query? Say 'Y' to run, 'N' to cancel.

SQL Query:
{sql_query}

==================================================================
        """)
        input_a = input()
        run_sql_query(0, input_a)

    def run_sql_query(stop, input_a):
        global sql_query  # Use the global sql_query variable
        if input_a.upper() == "Y":
            explain_prediction = "Connecting..."
            print(explain_prediction)
            try:
                # Use your actual MySQL credentials here
                con = mysql.connector.connect(host="localhost", user="your_user", password="your_password", database="datable")
                cursor = con.cursor()

                cursor.execute(sql_query)
                table = cursor.fetchall()
                explain_prompt_formatted_str: str = explain_prompt.format(sql_result=table)
                explain_prediction = llm.predict(explain_prompt_formatted_str)
                print(explain_prediction)
            except Exception as e:
                explain_prediction = f"An exception occurred: {e}"
                print(explain_prediction)
        else:
            explain_prediction = "Cancel. No action has been taken."
            print(explain_prediction)

def personnel_management():
    print("Personnel Management functionality is currently under development.")

# Start the CLI
if __name__ == "__main__":
    while True:
        cli()