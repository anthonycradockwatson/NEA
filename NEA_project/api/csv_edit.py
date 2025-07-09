import os
import sys

import pandas as pd  
from django.db import connection, transaction
from sql_checkers import uuid_verifier
import os

# Add the project root to sys.path so NEA_project can be found as a module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT NOTE FOR EXAMINER OR ANYONE READING THIS CODE:
# Originally the db was set up where it had a cars table, but then a new file with a bunch of vehicle models was found and chosen to 
# replace the old one since it had a bunch of extra information that was useful reccommendations so any references to the old table
# were only used prior to the tables deletion :)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NEA_project.settings')

def change_csv():
    # only getting relevant csv fields
    csv_path = r"C:\Users\antho\PycharmProjects\NEA\all-vehicles-model.csv"
    df = pd.read_csv(csv_path)

    necessary_fields = ['Make', 'Model', 'Year', "Drive", "Cylinders", "Engine displacement", "Transmission", "Vehicle Size Class"]
    df=df[necessary_fields]
    df.to_csv(r"updated_models.csv", index=False)

def csv_to_sql():

    with connection.cursor() as sql:
        sql.execute("""
            CREATE TABLE IF NOT EXISTS Vehicle_Models (
                vehicle_model_id VARCHAR (40) PRIMARY KEY,
                make VARCHAR(50),
                model VARCHAR(50),
                year INTEGER,
                drive VARCHAR(40),
                cylinders FLOAT,
                engine_displacement FLOAT,
                transmission VARCHAR(50),
                vehicle_size_class VARCHAR(50)
            )
        """)
        transaction.commit()

    csv_path = r"C:\Users\antho\PycharmProjects\NEA\updated_models.csv"
    df=pd.read_csv(csv_path) # This no longer works since cars got replaced with vehicle_models
    with connection.cursor() as sql:
        sql.execute("SELECT make, model, year FROM Cars")
        existing_cars = set(sql.fetchall())

    existing_cars_df = pd.DataFrame(list(existing_cars), columns=['Make', 'Model', 'Year'])
    df_filtered = df.merge(existing_cars_df, on=['Make', 'Model', 'Year'], how='inner') # essentially filters by (make, model, year)
    # to ensure the only entries left have the same (make, model, year), decreasing time taken for the for loop to run
    df_filtered = df_filtered.reset_index(drop=True)

    for x in range(len(df_filtered)): 

        make = str(df_filtered["Make"][x])
        model = str(df_filtered["Model"][x])
        year = int(df_filtered["Year"][x])
        drive = str(df_filtered["Drive"][x])
        cylinders = float(df_filtered["Cylinders"][x])
        engine_displacement = float(df_filtered["Engine displacement"][x])
        transmission = str(df_filtered["Transmission"][x])
        vehicle_size_class = str(df_filtered["Vehicle Size Class"][x])

        vehicle_model_id=uuid_verifier("Vehicle_Models", "vehicle_model_id")

        with connection.cursor() as sql:
            sql.execute("""
                INSERT INTO Vehicle_Models (vehicle_model_id, make, model, year, drive, cylinders, engine_displacement, transmission, vehicle_size_class)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [vehicle_model_id, make, model, year, drive, cylinders, engine_displacement, transmission, vehicle_size_class])
            transaction.commit()

print(csv_to_sql())
