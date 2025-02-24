import socket
from tools import *

def send_file_data_and_get_transaction_id(server_socket):
    send_string_file(server_socket, "secret_data1.txt")
    print("received transaction_id", server_socket.recv(5).decode())

def get_and_store_file_data(server_socket):
    pass

# Function to send a math expression to the server and get the result
def connect_to_server_and_store_info():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(('127.0.0.1', 5555))  # Connect to the server

    # send my id

    # ask user for 2 options  : STR or GET <TR_ID>
    option = input ("Please choose 1 for STORE or 2 for GET")

    if option == "1":
        tr_id = send_file_data_and_get_transaction_id(server_socket)
    elif option == "2":
        get_and_store_file_data(server_socket)


    # Close the connection
    server_socket.close()

if __name__ == "__main__":
    connect_to_server_and_store_info()