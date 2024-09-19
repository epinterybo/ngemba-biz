import psycopg2
import pymssql
import pandas as pd
import numpy as np
import os

# scripts/external_script.py
def run_script():
    print("External script executed")
    # PostgreSQL connection details
    pg_host = os.getenv("PGHOST")
    pg_dbname = os.getenv("PGDATABASE")
    pg_user = os.getenv("PGUSER")
    pg_password = os.getenv("PGPASSWORD")

    pg_table = "cw_ocm_forecast"

    # MSSQL connection details
    ms_host = "103.20.233.88"
    ms_port = 14140
    ms_user = "chris"
    ms_password = "acm39dsmso111ZZW"
    ms_database = "ChrisForecast"
    ms_table = "dbo.cw_ocm_forecast"

    try:
        # Connect to PostgreSQL
        print(f"Connecting to PostgreSQL database {pg_dbname} on {pg_host}...")
        pg_conn = psycopg2.connect(
            host=pg_host,
            dbname=pg_dbname,
            user=pg_user,
            password=pg_password
        )
        pg_cursor = pg_conn.cursor()

        # Fetch data from PostgreSQL
        pg_cursor.execute(f"SELECT * FROM {pg_table}")
        rows = pg_cursor.fetchall()

        # Get column names from PostgreSQL
        colnames = [desc[0] for desc in pg_cursor.description]

        # Create DataFrame
        df = pd.DataFrame(rows, columns=colnames)
        print(f"Fetched {len(df)} rows from PostgreSQL table {pg_table}.")
        print("DataFrame column types:")
        print(df.dtypes)

        # Handle NaN values
        df = df.replace({np.nan: None})

        # Format date columns
        date_columns = ['x_lastPurchaseOrderDate', 'x_lastReceivedTime', 'X_StockTakedate', 'x_timecreateditem', 'create_date', 'write_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if x is not None else None)

    except Exception as e:
        print(f"Error connecting to PostgreSQL or fetching data: {e}")
        exit(1)

    try:
        # Connect to MSSQL
        print(f"Connecting to MSSQL database {ms_database} on {ms_host}:{ms_port}...")
        ms_conn = pymssql.connect(
            server=ms_host,
            port=ms_port,
            user=ms_user,
            password=ms_password,
            database=ms_database
        )
        ms_cursor = ms_conn.cursor()
        
        # Clean the target MSSQL table
        print(f"Truncating MSSQL table {ms_table}...")
        ms_cursor.execute(f"TRUNCATE TABLE {ms_table}")
        ms_conn.commit()
        
        # Insert data into MSSQL in batches of 1000
        batch_size = 1000
        for start in range(0, len(df), batch_size):
            end = min(start + batch_size, len(df))
            batch = df.iloc[start:end]
            
            values_list = []
            for index, row in batch.iterrows():
                values = ', '.join(f"""'{str(val).replace("'", '')}'""" if val is not None else 'NULL' for val in row.values)
                values_list.append(f"({values})")
            
            columns = ', '.join(batch.columns)
            insert_query = f"INSERT INTO {ms_table} ({columns}) VALUES {', '.join(values_list)}"
            print(f"Executing insert query for batch {start} to {end}...")
            #print(insert_query)  # Print the query to debug

            ms_cursor.execute(insert_query)
            ms_conn.commit()
        print("Data inserted successfully.")

    except pymssql.OperationalError as e:
        print(f"MSSQL OperationalError: {e}")
    except Exception as e:
        print(f"Error connecting to MSSQL or inserting data: {e}")
    finally:
        # Close connections
        pg_cursor.close()
        pg_conn.close()
        ms_cursor.close()
        ms_conn.close()

if __name__ == "__main__":
    run_script()
