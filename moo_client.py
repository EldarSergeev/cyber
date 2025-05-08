import socket
from tools import *
from encryption_lib import Encryption2





def send_file_data_and_get_transaction_id(server_socket):
    encrypted_start = eObj.encrypt_data("STR", server_public_key)  
    print ("encrypted:", encrypted_start)
    server_socket.send(encrypted_start)
    send_string_file(server_socket, "secret_data1.txt",eObj, server_public_key, client_private_key)
    encrypted_transaction_id = server_socket.recv(256)  # Adjust buffer size
    transaction_id = eObj.decrypt_data(encrypted_transaction_id, client_private_key)
    print("Received transaction ID:", transaction_id)

def get_and_store_file_data(server_socket):
    encrypted_get = eObj.encrypt_data("GET", server_public_key)
    server_socket.send(encrypted_get)
    encrypted_options = server_socket.recv(256)
    options = eObj.decrypt_data(encrypted_options, client_private_key)
    selected_option=input("please select the file you want to get:"+options)
    encrypted_selection = eObj.encrypt_data(selected_option, server_public_key)
    server_socket.send(encrypted_selection)
    with open("new_file","w") as file:
        print("Receiving data...")
        encrypted_data = server_socket.recv(256)
        while encrypted_data:
            decrypted_data = eObj.decrypt_data(encrypted_data, client_private_key)
            file.write(decrypted_data) 
            encrypted_data = server_socket.recv(256)
    print("all data has been recived")

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
    eObj = Encryption()
    server_public_key = eObj.load_server_public_key()
    client_private_key = eObj.load_client_private_key()
    connect_to_server_and_store_info()