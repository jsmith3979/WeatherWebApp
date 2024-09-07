import mysql.connector
from mysql.connector import Error

# Establish connection to MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',        
            user='root',
            password='darkknight3979',
            database='weather_app'
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