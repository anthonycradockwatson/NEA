from django.db import connection
def validation(category):        
    allowed_categories = {"Wheels", "Spoilers", "Front_Bumpers", "Rear_Bumpers", "Grills"}
    if set(category).issubset(allowed_categories) == False:
        return False
    
def sql_check(id, table, column_name):

    if type(id) != list:
        if len([id]) == 1:
            id=[id]
        else:
            id=list(id)

    with connection.cursor() as sql:
        sql.execute(f"Select {column_name} from {table}")
        allowed_ids=set(row[0] for row in sql.fetchall())
    if set(id).issubset(allowed_ids) == False:
        return False

    
