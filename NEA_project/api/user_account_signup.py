from .sql_checkers import uuid_verifier, existing_entry
from .input_cleansing import input_cleansing
from django.db import connection,transaction
def user_signup_check(email, password, car_id):

    # Check if the email and password contain banned characters
    email_cleansing=input_cleansing(email, True)
    password_cleansing=input_cleansing(password, False)
    if email_cleansing==False or password_cleansing==False:
        return "Input contains banned characters"

    # ensuring tables are created
    with connection.cursor() as sql:
        sql.execute("""
            CREATE TABLE IF NOT EXISTS User_accounts (
                account_id VARCHAR(40) PRIMARY KEY,
                email VARCHAR(100), 
                password VARCHAR(50), 
                car_id VARCHAR(40),
                FOREIGN KEY (car_id) REFERENCES Vehicle_Models(vehicle_model_id)
            )
        """)
    transaction.commit()
    
    valid_new_email=existing_entry(email, "user_accounts", "email") 
    # checks if account with email already exists
    if not valid_new_email:
        return "Email already exists"
    
    else:
        account_id=uuid_verifier("User_accounts", "account_id")
        # if the account_id, email and password are valid, inserts the new user into the database
        with connection.cursor() as sql:
            sql.execute(f"INSERT INTO User_accounts (account_id, email, password, car_id) VALUES (%s, %s, %s, %s)", [account_id, email, password, car_id])
            transaction.commit()
        return True 
    
