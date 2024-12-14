import pyodbc
import os
from dotenv import load_dotenv

# function to create a connection to the database
def create_connection(username=None, password=None):
    # load the environment variables
    load_dotenv()
    
    # get the connection string
    server = os.getenv('DB_SERVER')
    if username is None:
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
    
    database = os.getenv('DB_NAME')
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # try to connect to the database
    try:
        # create the connection
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        # print the error if there is one
        print(f'Error: {e}')
        return None