from django.db import connection
def validation(category, user_id=None, manufacturers = None):

    if manufacturers:
        with connection.cursor() as sql:
            sql.execute(f"Select merchant_name from Parts")
            allowed_manufacturers=set(row[0] for row in sql.fetchall())
        if set(manufacturers).issubset(allowed_manufacturers) == False:
            return False
        
    if user_id:
        with connection.cursor() as sql:
            sql.execute(f"Select account_id from User_Accounts")
            allowed_users=sql.fetchall()
        if user_id not in allowed_users:
            return False
        
    allowed_categories = {"Wheels", "Spoilers", "Front_Bumpers", "Rear_Bumpers", "Grills"}
    if set(category).issubset(allowed_categories) == False:
        return False
    

    
