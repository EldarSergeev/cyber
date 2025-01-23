import socket
import threading
from db_tools import *    

host = '127.0.0.1'
mydb = init()
create_database(mydb, "mysql")
mydb_db = init_with_db("mysql")
create_table(mydb_db, "data_user",
                 "(id INT, ip VARCHAR(255), port INT, Isblacklisted TINYINT(1),Connections_per_day INT )")
create_table(mydb_db, "transections",
                 "(src_id INT, timeset VARCHAR(255), password VARCHAR(255), is_succeded TINYINT(1), trans_id INT, char_1 VARCHAR(255), char_2 VARCHAR(255), char_3 VARCHAR(255), char_4 VARCHAR(255), char_5 VARCHAR(255))")




def handle_client_request(message, password):
    if message!="request":
        try:
            result = [c for c in message if c != ' ']
            if len(result)>5:
                raise Exception("your message is too long")
        finally:
            






# Function to handle client communication
def handle_client(client_socket):
    try:
        # Receive the expression from the client
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            return
        
        # Try to evaluate the math expression
        try:
            result = eval(data)  
            client_socket.send(f"Result: {result}".encode('utf-8'))
        except Exception as e:
            client_socket.send(f"Error in expression: {e}".encode('utf-8'))
    finally:
        # Close the connection after the transaction
        client_socket.close()

# Set up the server
def start_server(host='127.0.0.1', port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}...")
    
    while True:
        # Accept new client connections
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")
        
        # Create a new thread to handle the client request
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()