import sqlite3
import psycopg2
import uuid
from django.db import connection
def existing_entry(entry, table, column_name): # This function checks if a given entry/name already 
    # exists in the specified table and column.
    valid_entry=True

    with connection.cursor() as sql:
        sql.execute(f"SELECT * FROM {table} WHERE {column_name} = '{entry}'")
        entry_exists=sql.fetchall()
        
    if entry_exists:

        valid_entry = False

    return valid_entry

def uuid_verifier(table, id_column): # This function generates a unique UUID and checks it against the existing IDs in the specified table.
    valid_id=False

    while valid_id==False:

        id=str(uuid.uuid4())

        with connection.cursor() as sql:
            sql.execute(f"SELECT * FROM {table} WHERE '{id_column}' = '{id}'")
            id_exists=sql.fetchall()

        if not id_exists:
            valid_id=True
    return id
