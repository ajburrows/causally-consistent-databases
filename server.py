import socket
import threading
import time
import mysql.connector
import configvals


class Server:
    def __init__(self, port, datacenters, db_name):
        self.HOST = "127.0.0.1"
        self.PORT = port 
        self.clients = {}
        self.connect_to_database(db_name)
        print(f"Connected to database {self.db_name} for Server {self.PORT}")
        self.add_datacenters(datacenters)
    
        
    def connect_to_database(self, db_name):
        self.db_name = db_name
        self.db_connection = mysql.connector.connect(host=configvals.DB_HOST, user=configvals.DB_USER, password=configvals.DB_PASSWORD, database=db_name)
        self.db_cursor = self.db_connection.cursor()


    def store_dependency(self, dependency_key):
        # Used to store a dependency key in this server's database
        try:
            self.db_cursor.execute("INSERT INTO dependencies (dependency_key) VALUES (%s)", (dependency_key,))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            print(f'Error storing dependency: {err}')
    

    def store_message(self, key, value):
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(host=configvals.DB_HOST, user=configvals.DB_USER, password=configvals.DB_PASSWORD, database=self.db_name)
            cursor = connection.cursor()

            cursor.execute("INSERT INTO messages (dependency_key, content) VALUES (%s, %s)", (key, value))
            connection.commit()

        except mysql.connector.Error as err:
            print(f'Error in storing message: {err}')

        finally:
            if connection:
                connection.close()
            if cursor:
                cursor.close()
    

    def get_all_dependencies(self):
        # Get all the dependencies from the database
        try:

            self.db_cursor.execute("SELECT dependency_key FROM dependencies")
            dependencies = [row[0] for row in self.db_cursor.fetchall()]
            return dependencies
        except mysql.connector.Error as err:
            return []


    def check_dependency_exists(self, dependency_key):
        # Check if a specific dependency exists in the database
        try:
            self.db_cursor.execute(
                "SELECT 1 FROM dependencies WHERE dependency_key = %s", (dependency_key,)
            )
            exists = self.db_cursor.fetchone() is not None
            return exists
        except mysql.connector.Error as err:
            print(f'Error checking dependency: {err}')
            return False


    def add_datacenters(self, datacenters):
        try:
            insert_query = "INSERT INTO data_centers (dc_port) VALUES (%s)"
            for dc_port in datacenters:
                self.db_cursor.execute(insert_query, (dc_port,))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            print(f'\nError storing datacenter ports\n')


    def get_all_datacenters(self, cursor):
        try:
            query = "SELECT dc_port FROM data_centers"
            cursor.execute(query)
            rows = cursor.fetchall()
            data_centers = [row[0] for row in rows]
            return data_centers

        except mysql.connector.Error as err:
            print(f'Error retreiving datacenters: {err}')
            return []


    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            print(f"Server listening on {self.HOST}:{self.PORT}")
            
            while True:
                conn, addr = s.accept()  # Accept a new connection
                # Start a new thread to handle the client
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()
    

    def check_dependencies(self, dependency_list):
        # looks through every dependency key in dependency_list and checks if that message is already stored
        #print(f'\nCHECKING DEPENDENCIES\nself.storage: {self.storage}, dependency_list: {dependency_list}')
        for key in dependency_list:
            if key == '':
                continue
            self.db_cursor.execute("SELECT 1 FROM messages WHERE dependency_key = %s LIMIT 1", (key,))
            res = self.db_cursor.fetchone()
            if not res:
                return False
        return True


    def handle_client(self, conn, addr):
        with conn:
            while True:
                data = conn.recv(1024).decode('utf-8')  # Receive data from the client
                if not data:
                    break
                
                #Send an acknowledgment message back to the client
                port, op, message = data.split(':')
                print(f'op: {op}, message: {message}')
                print(f"Starting {op} for Client {port}")
                if op == "RegisterRequest":
                    self.RegisterClient(port)
                elif op == "REPLICATE":
                    print(f"REPLICATING: {message[0]}")
                    write, dependency = message.split('-')
                    print(f"Dependency == {dependency}")
                    dependency = dependency[1:-1].split(',')
                    dependency = [key.strip('\'') for key in dependency]
                    
                    delayed = False
                    #while not all(message in self.storage for message in dependency):
                    while self.check_dependencies(dependency) == False:
                        print(f"Server {self.PORT}: DEPENDENCY {dependency} NOT FOUND, Delaying replication until dependency satisfied")
                        delayed = True
                        time.sleep(2)
                    if delayed:
                        print("Dependency has been satisfied, writing message to storage")
                    self.writeToStorage(write, replicate=False)
                    
                elif op == "WRITE":
                    self.writeToStorage(message)

                elif op == "READ":
                    pass

                response = f"{op} from {port} completed"

                conn.send(response.encode('utf-8'))


    def send_to_server(self, message, server_port):
        #Method to connect to the central server and send a message
        message = f"{self.PORT}:{message}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            server_host = '127.0.0.1'

            try:
                #Connect to the central server, then send a message
                s.connect((server_host, server_port))
                print(f"Replicating message to {server_port}")
                s.send(message.encode('utf-8'))
                
                # Wait for a response from the server
                response = s.recv(1024).decode('utf-8')
                parsed_response = response.split(" ")
                

                print(f"Server response: {response}")
            except ConnectionRefusedError:
                print(f"Failed to connect to server at {server_host}:{server_port}")
            except Exception as e:
                print(f"An error occurred: {e}")


    def RegisterClient(self, client_port):
        if client_port not in self.clients:
            self.clients[client_port] = {}
        else:
            print("ERROR: CLIENT ALREADY REGISTERED")
        


    def writeToStorage(self, message, replicate=True, delay=False):
        # Write to the dictionary in memory
        key, value = message.split(',')
        print(f'\nkey: {key}\nvalue: {value}\n')
        self.store_message(key, value)

        message_with_dep = f"{message}-{self.get_all_dependencies()}"
        if replicate:
            threading.Thread(target=self.ReplicateWrite, args=(message_with_dep, True if message[0] == 'x' else False)).start()

        self.store_dependency(key)
        print(f'Message written to storage: {message}')



    # ReplicateWrite is only instance where a thread will create concurrent queries to the database. Due to this we must create a new connection
    # for ReplicateWrite to use and close it when the method is complete.
    def ReplicateWrite(self, message, delay=False):
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(host=configvals.DB_HOST, user=configvals.DB_USER, password=configvals.DB_PASSWORD, database=self.db_name)
            cursor = connection.cursor()
            message = f"REPLICATE:{message}"
            all_datacenters = self.get_all_datacenters(cursor)
            
            for datacenter in all_datacenters:
                if delay:
                    print(f"Delaying message to {datacenter}")
                    print(message)
                    time.sleep(3)
                self.send_to_server(message, datacenter)

        except mysql.connector.Error as err:
            print(f'Error replicating write: {err}')

        finally:
            if connection:
                connection.close()
            if cursor:
                cursor.close()