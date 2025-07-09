
from .input_cleansing import input_cleansing
from django.db import connection, transaction
def account_login(email, password):
    

    # Check if the email and password contain banned characters
    email_cleansing=input_cleansing(email, True)
    password_cleansing=input_cleansing(password, False)
    
    if email_cleansing==False or password_cleansing==False:
        return "Input contains banned characters"
    
    # Finds users account
    with connection.cursor() as sql:
        sql.execute(f"SELECT * FROM User_accounts WHERE email = %s AND password = %s", (email, password))
        account_exists = sql.fetchall()

    if account_exists:
        return True
    else:
        # Returns false if either password or email is incorrect or if account does not exist
        return False
