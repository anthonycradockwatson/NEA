from .sql_checkers import uuid_verifier
import pandas as pd  
from django.db import connection, transaction

def add_car(make, model, year, cylinders, engine_displacement, transmission):
    with connection.cursor() as sql:
        sql.execute("""CREATE TABLE IF NOT EXISTS Vehicle_Models
                    (
                    vehicle_model_id VARCHAR(40) PRIMARY KEY, 
                    make VARCHAR(100), 
                    model VARCHAR(100), 
                    year INTEGER, 
                    drive VARCHAR(100),
                    cylinders FLOAT,
                    engine_displacement FLOAT,
                    transmission VARCHAR(100),
                    vehicle_size_class VARCHAR(100)
                    )""")
        transaction.commit()


    csv_path = r"C:\Users\antho\PycharmProjects\NEA\updated_models.csv"
    df=pd.read_csv(csv_path)

    with connection.cursor() as sql:
        sql.execute("SELECT make, model, year, cylinders, engine_displacement, transmission FROM Vehicle_Models")
        existing_cars = set(sql.fetchall())

    # Only add if not already in DB
    if (make, model, year, cylinders, engine_displacement, transmission) not in existing_cars:
        # Find the row in the CSV
        row = df[(df["Make"] == str(make)) & (df["Model"] == str(model)) & (df["Year"] == int(year)) & (df["Cylinders"] == float(cylinders)) & (df["Engine displacement"] == float(engine_displacement)) & (df["Transmission"] == str(transmission))]
        if not row.empty:   
            row = row.iloc[0]
            drive = str(row["Drive"])
            vehicle_size_class = str(row["Vehicle Size Class"])
            vehicle_model_id = uuid_verifier("Vehicle_Models", "vehicle_model_id")
            with connection.cursor() as sql:
                sql.execute("""
                    INSERT INTO Vehicle_Models (vehicle_model_id, make, model, year, drive, cylinders, engine_displacement, transmission, vehicle_size_class)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [vehicle_model_id, make, model, year, drive, cylinders, engine_displacement, transmission, vehicle_size_class])
                transaction.commit()
            return vehicle_model_id
        else:
            return None  # Car not found in CSV
    else: # If the car exists already it returns the existing car id
        with connection.cursor() as sql:
            sql.execute("""
                SELECT vehicle_model_id FROM Vehicle_Models
                WHERE make=%s AND model=%s AND year=%s AND cylinders=%s AND engine_displacement=%s AND transmission=%s
            """, [make, model, year, cylinders, engine_displacement, transmission])
            car_id = sql.fetchone()[0]
            return car_id
