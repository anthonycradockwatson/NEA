import json
import re
from sql_checkers import uuid_verifier, existing_entry
from django.db import connection, transaction
import os
import sys
def json_sql_convert(data_file):

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NEA_project.settings')

    with open(data_file, "r") as carparts: # accessing json file of new items to be added
        data = json.load(carparts)
    data=data["categories"]

    # creating unique category part tables
    with connection.cursor() as sql:
        sql.execute(f"""
            CREATE TABLE IF NOT EXISTS Parts
                    (
                        part_id VARCHAR(40) PRIMARY KEY,
                        category VARCHAR(40),
                        item_name VARCHAR(100),
                        merchant_name VARCHAR(100),
                        image_url_medium VARCHAR(255),
                        price INTEGER,
                        is_sponsored INTEGER
                        )
        """)
        transaction.commit()

    for x in range(len(data)):

        current_category_name=data[x]["category_name"]  # Selects the current category of part

        current_category=data[x]["items"]

        for i in range(len(current_category)): # Iterates through all items in category

            size_uuid, colour_uuid = None, None

            part_uuid=uuid_verifier("Parts", "part_id")
            partid = f"{current_category_name[0]}-{part_uuid}"
            
            # collecting all the part data

            item_name = current_category[i].get("item_name")
            merchant_name = current_category[i].get("merchant_name")
            image_url_medium = current_category[i].get("image_url_medium")
            price = int(current_category[i].get("price")[1:])
            is_sponsored = int(current_category[i].get("is_sponsored", 0))

            # Inputting all parts into parts table      
            with connection.cursor() as sql:
                sql.execute(f"""
                        INSERT INTO Parts (part_id, category, item_name, 
                        merchant_name, image_url_medium, price, is_sponsored)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            [partid, current_category_name ,item_name, merchant_name, image_url_medium, price, is_sponsored])
                transaction.commit()

            # collecting size and colour variants

            size_stack = json.dumps(current_category[i].get("size_stack"))
            size_stack = re.split('{|}',size_stack)
            colour_stack = json.dumps(current_category[i].get("color_stack"))
            colour_stack = re.split('{|}',colour_stack)

                # formatting size and colour info and identifying which is bigger so that if an item has colour variations
                # but not size variations, it still registers all the colours and sizes

            size_stack = size_stack[2:-1:2]
            colour_stack = colour_stack[2:-1:2]
            with connection.cursor() as sql:
                sql.execute(f"""
                    CREATE TABLE IF NOT EXISTS Sizes
                        (
                        size_id VARCHAR (40) PRIMARY KEY,
                        size VARCHAR (10),
                        size_unit VARCHAR (10)
                        )
                """)
        
                sql.execute(f"""
                    CREATE TABLE IF NOT EXISTS Colours
                        (
                        colour_id VARCHAR(40) PRIMARY KEY,
                        colour VARCHAR (50)
                        )
                """)
                transaction.commit()

            # Creating a link table to link the parts with their sizes and colours when needed

            link_table_name = f"{current_category_name}_link_table"
            if size_stack != [] or colour_stack != []:
                with connection.cursor() as sql:
                    sql.execute(f"""
                        CREATE TABLE IF NOT EXISTS {link_table_name}
                            (
                            {link_table_name}_id VARCHAR (40) PRIMARY KEY,
                            {current_category_name}_id VARCHAR(40),
                            size_id VARCHAR(40),
                            colour_id VARCHAR(40),
                            colour_image_url VARCHAR (255),
                            FOREIGN KEY ({current_category_name}_id) REFERENCES Parts(part_id),
                            FOREIGN KEY (size_id) REFERENCES sizes(size_id),
                            FOREIGN KEY (colour_id) REFERENCES colours(colour_id)
                            )
                    """)
                    transaction.commit()

                # This will avoid indexing issues if the # of sizes != # of colours
            if len(size_stack)>len(colour_stack):
                big_fit_options=len(size_stack)
                small_fit_options=len(colour_stack)
                most_options="size"
            else:
                big_fit_options = len(colour_stack)
                small_fit_options = len(size_stack)
                most_options = "colour"
            if small_fit_options == 0:
                small_fit_options=1

                # looping through all possible item combinationsn without repeats

            for y in range(big_fit_options):
                for z in range(small_fit_options):

                    # more size and colour info formatting

                    if size_stack != []:
                        if most_options=="size":
                            size_options=size_stack[y].split()
                        else:
                            size_options=size_stack[z].split()
                        size_options=size_options[1::2]
                        size = size_options[0][:-1]
                        size_unit = size_options[1][1:-1]
                    else:
                        size, size_unit=None, None

                    if colour_stack != []:
                        if most_options=="colour":
                            colour_options=colour_stack[y].split()
                        else:
                            colour_options = colour_stack[z].split()
                        colour_options=colour_options[1::2]
                        colour = colour_options[0][:-1]
                        colour_image = colour_options[1][1:-1]
                    else:
                        colour, colour_image = None, None

                    # Inputting all the size and colour data into their respective tables
                    if size_stack != []:

                        existing_size = existing_entry(size, "Sizes", "size") # Checks if the size combo exists
                        existing_size_unit = existing_entry(size_unit, "Sizes", "size_unit")
        
                        if existing_size == True or existing_size_unit == True:
                            
                            size_uuid=uuid_verifier("Sizes", "size_id")
                            # If does not yet exist, it gets entered into the table with the new verified uuid
                            with connection.cursor() as sql:
                                sql.execute(f"""    
                                    INSERT INTO Sizes (size_id, size, size_unit)
                                    VALUES (%s, %s, %s)""",
                                    [size_uuid, size, size_unit]
                                    )
                                transaction.commit()
                
                        else: # If it does the size_uuid just becomes the existing one 
                            with connection.cursor() as sql:
                                sql.execute(f"SELECT size_id FROM Sizes WHERE size = '{size}' AND size_unit = '{size_unit}'")
                                size_uuid=sql.fetchone()[0]
                    
                    if colour_stack != []:  # Same layout as the size for the colours, just now only checks 1 thing
                    
                        existing_colour = existing_entry(colour, "Colours", "colour")

                        if existing_colour == True:

                            colour_uuid=uuid_verifier("Colours", "colour_id")

                            with connection.cursor() as sql:
                                sql.execute(f"""
                                    INSERT INTO Colours (colour_id, colour)
                                    VALUES (%s, %s)""",
                                    [colour_uuid, colour]
                                    )
                                transaction.commit()
    
                        else:
                            with connection.cursor() as sql:
                                sql.execute(f"SELECT colour_id FROM Colours WHERE colour = '{colour}'")
                                colour_uuid=sql.fetchone()[0]
            
                    link_uuid=uuid_verifier(link_table_name, f"{link_table_name}_id")
                    # makes the links between the parts and their sizes and colours, with the colour-specific images being stored here
                    with connection.cursor() as sql:
                        sql.execute(f"""
                            INSERT INTO {link_table_name} ({link_table_name}_id, {current_category_name}_id, 
                            size_id, colour_id, colour_image_url)
                            VALUES (%s, %s, %s, %s, %s)""",
                                [link_uuid, partid, size_uuid, colour_uuid, colour_image]
                        )
                        transaction.commit()

    return("Data Transfer Success")
print(json_sql_convert("data4.json"))