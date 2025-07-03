import sqlite3
from .sql_checkers import uuid_verifier
from django.db import connection, transaction

def user_liked(part_id, account_id):

    committed=False
    with connection.cursor() as sql:
        sql.execute(f"""
            CREATE TABLE IF NOT EXISTS User_likes 
                    (
                        like_id VARCHAR(40) PRIMARY KEY,
                        account_id VARCHAR(40),
                        liked_part_id VARCHAR(40),
                        FOREIGN KEY (account_id) REFERENCES User_accounts(account_id),
                        FOREIGN KEY (liked_part_id) REFERENCES Parts(part_id)
                    )
            """)
        transaction.commit()

    if len(part_id) == 1:
        tuple_part_id=part_id[0],''
    else:
        tuple_part_id=tuple(part_id)

    for x in range(len(part_id)):

        with connection.cursor() as sql:

            sql.execute(f"SELECT liked_part_id FROM User_likes WHERE account_id='{account_id}' AND liked_part_id IN {tuple_part_id}")
            existing_likes_id = {row[0] for row in sql.fetchall()}
                  
        if set([part_id[x]]).issubset(existing_likes_id) == False:

            like_uuid=uuid_verifier("User_likes", "like_id")

            with connection.cursor() as sql:
                sql.execute(f"""
                            INSERT INTO User_likes VALUES (%s, %s, %s)""",
                            [like_uuid, account_id, part_id[x]]
                            )
                transaction.commit()
            committed=True

        
    return committed

def user_unlike(part_id, account_id):

    if len(part_id) == 1:
        tuple_part_id=(part_id[0],'')
    else:
        tuple_part_id=tuple(part_id)

    committed=False
    for x in range(len(part_id)):

        with connection.cursor() as sql:

            sql.execute(f"SELECT liked_part_id FROM User_likes WHERE account_id='{account_id}' AND liked_part_id IN {tuple_part_id}")
            existing_likes_id = {row[0] for row in sql.fetchall()}

        if set([part_id[x]]).issubset(existing_likes_id) == True:
            
            with connection.cursor() as sql:
                sql.execute(f"DELETE FROM user_likes WHERE liked_part_id = '{part_id[x]}'")
                transaction.commit()
            committed=True
    return committed
