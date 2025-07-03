from django.db import connection

def item_collect(category, manufacturers):

    # Execute the SQL query to collect items from the specified category
    if len(manufacturers) == 1:
        manufacturers = (manufacturers[0],'') 
    else:
        manufacturers = tuple(manufacturers)

    if len(category) == 1:
        category = (category[0],'')
    else:
        category = tuple(category)

    with connection.cursor() as sql:
        sql.execute(f"SELECT * FROM Parts WHERE category IN {category} AND merchant_name IN {manufacturers}")
        results = sql.fetchall()

    # Close the database connection

    return results
