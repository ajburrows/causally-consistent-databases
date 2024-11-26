import mysql.connector
import configvals

def clear_database(db_name):
    try:
        connection = mysql.connector.connect(host=configvals.DB_HOST, user=configvals.DB_USER, password=configvals.DB_PASSWORD, database=db_name)
        cursor = connection.cursor()
        
        # get a list of the tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # clear the tables
        for (table_name,) in tables:
            cursor.execute(f'TRUNCATE TABLE {table_name}')
            print(f'Cleared table: {table_name}')
        
        connection.commit()
        print(f'Cleared all tables in database {db_name}')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        print(f'Failed to clear database {db_name}')
        if connection:
            connection.close()
    

databases = ["server1", "server2"]
for db in databases:
    clear_database(db)

def main():
    print("clear_databases: running main()")
    for db in databases:
        clear_database(db)