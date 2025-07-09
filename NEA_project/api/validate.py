from django.db import connection
def validation(category):       
    # This is to ensure that the category sent by the frontend
    if type(category) != list: # turns everything into a list to then turn it into a set
        if len([category]) == 1:
            category=[category]
        else:
            category=list(category)

    allowed_categories = {"Wheels", "Spoilers", "Front_Bumpers", "Rear_Bumpers", "Grills"}

    if set(category).issubset(allowed_categories) == False: # If categories given aren't a subset of all the valid ones
        # then the categories arent valid
        return False
    
def sql_check(id, table, column_name): # basically checking that ids are valid

    if type(id) != list: # to normalise a list of ids or just one id
        if len([id]) == 1:
            id=[id]
        else:
            id=list(id)

    with connection.cursor() as sql:
        sql.execute(f"Select {column_name} from {table}")
        allowed_ids=set(row[0] for row in sql.fetchall())
    if set(id).issubset(allowed_ids) == False: # does the same thing as the validation but with a list of every valid id
        return False

    
def all_categories(category): # getting every category or manufacturer to allow for ["*"] to be passed from the frontend

    with connection.cursor() as sql:
        sql.execute(f"SELECT DISTINCT {category} FROM parts")
        all_categories=sql.fetchall()
        all_categories=[item[0] for item in all_categories]

    return all_categories
