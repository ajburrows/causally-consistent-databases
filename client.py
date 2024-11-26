import socket
import threading

class Client:
    def __init__(self, port, datacenter_port):
        #Initialize peer with a port and an optionl file to share
        self.host = "127.0.0.1"
        self.port = port
        self.datacenter_port = datacenter_port


    def start_server(self):
        #Start up the peer and listen for incoming requests
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Peer listening on {self.host} : {self.port}")
            
            while True:
                conn, addr = s.accept()
                # Start a new thread to handle the new client
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()
    

    def send_to_server(self, write):
        #Method to connect to the central server and send a message
        message = f"{self.port}:{write}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            server_host = '127.0.0.1'

            try:
                #Connect to the central server, then send a message
                s.connect((server_host, self.datacenter_port))
                print(f"Client {self.port} Sending {write} to server...")
                #print(message)
                s.send(message.encode('utf-8'))
                
                # Wait for a response from the server
                response = s.recv(1024).decode('utf-8')
                parsed_response = response.split(" ")


                print(f"Server response: {response}")
                print('\n')
            except ConnectionRefusedError:
                print(f"Failed to connect to server at {server_host}:{self.datacenter_port}")
            except Exception as e:
                print(f"An error occurred: {e}")
    

    def writeToDataCenter(self, message):
        self.send_to_server(f"WRITE:{message}")


    def registerWithServer(self):
        self.send_to_server(write="RegisterRequest:[]")