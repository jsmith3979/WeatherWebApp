import mysql.connector
from mysql.connector import Error

# Establish connection to MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',        # or '127.0.0.1' if using localhost
            user='root',             # your MySQL username
            password='darkknight3979',# your MySQL password
            database='weather_app' # the database you want to connect to
        )
        if connection:
            print("Connection object created")

        if connection.is_connected():
            print("Connected to MySQL server")
            return connection
        else:
            print("Connection failed: Not connected.")
    except Error as e:
        print(f"Error: {e}")
    return None

# Call the function
conn = create_connection()