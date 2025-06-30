import sqlite3
from django.db import connection

def item_data(part_id, table):
    
    link_table_name = f"{table.lower()}_link_table"

    # Check if the table exists
    with connection.cursor() as sql:
        sql.execute(f"SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND tablename = %s", (link_table_name,))
        link_table_exists = bool(sql.fetchone()[0])
    # If the link table exists, proceed to get sizes and colours

    if link_table_exists:
        # Selects all the size ids which are linked to the part id in the link table
        with connection.cursor() as sql:
            sql.execute(f"SELECT size_id FROM {link_table_name} WHERE {table}_id = %s", (part_id,))
            size_ids = sql.fetchall()

        # gets all the size variations by the given size ids
        item_sizes=[]
        size_ids = tuple(size_id[0] for size_id in size_ids)
        if len(size_ids) == 1:
            size_ids = (size_ids[0])
#
        with connection.cursor() as sql:
            sql.execute(f"SELECT size, size_unit FROM Sizes WHERE size_id in {size_ids}")
            size_returns = sql.fetchall()
  
        if size_returns:
            for x in range(len(size_returns)):
                if size_returns[x] not in item_sizes:
                    item_sizes.append(size_returns[x])



        # Same process for colours
        with connection.cursor() as sql:
            sql.execute(f"SELECT colour_id FROM {link_table_name} WHERE {table}_id = %s", (part_id,))
            colour_ids = sql.fetchall()

        item_colours=[]
        colour_ids = tuple(colour_id[0] for colour_id in colour_ids)
        if len(colour_ids) == 1:
            colour_ids = (colour_ids[0])
     
        with connection.cursor() as sql: 
            sql.execute(f"SELECT colour FROM Colours WHERE colour_id in {colour_ids}")
            colour_returns = sql.fetchall()

        if colour_returns:
            for x in range(len(colour_returns)):
                if colour_returns[x][0] not in item_colours:
                    item_colours.append(colour_returns[x][0])
    else:
        # If the link table does not exist, set item_sizes and item_colours to empty lists
        item_sizes = []
        item_colours = []

    # Gets the part data to be returned alongside the sizes and colours
    with connection.cursor() as sql:
        sql.execute(f"SELECT * FROM Parts WHERE part_id = %s", (part_id,))
        part_data= sql.fetchall()[0]
   
    return part_data, item_colours, item_sizes
