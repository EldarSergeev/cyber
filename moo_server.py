import socket
import threading
import random
from db_tools import *    
from tools import *
from encryption_lib import Encryption
from server_UI import TransactionViewer
import tkinter as tk
from tkinter import ttk

client_sockets = {}




def start_ui():
    root = tk.Tk()
    viewer = TransactionViewer(root)
    root.mainloop()
# Function to handle client communication
def handle_client(db, client_socket,client_address):
    (ip, port) = client_address

    if ip not in client_sockets:
        client_sockets[ip] = []
    client_sockets[ip].append(client_socket)
    print(f"Stored socket for {ip}. Total sockets from this IP: {len(client_sockets[ip])}")
    try:

        # receive option STR/GET
        
        encrypted_option = client_socket.recv(256)
        option = eObj.decrypt_data(encrypted_option, server_private_key)
        (ip, port) = client_address
        all_clients = get_all_rows(db, "clients")
        # for now client is identified by ip only
        client_id = -1
        for (id , client_ip , client_port, ddos_status , timestamp ) in all_clients:
            if ip == client_ip: # found our client
                if get_rows_from_table_with_value(db,"clients","ip",ip)[0][3]==True:
                    message="connection denied dropping..."
                    encrypted_message=eObj.encrypt_data(message, client_public_key)
                    client_socket.send(encrypted_message)
                    client_socket.close()

                client_id = id
                delete_row(db, "clients", "client_id", (str(id) ))
                insert_row(db, "clients",
                    "(client_id, ip, port, ddos_status, timestamp)",
                    "(%s, %s, %s, %s, %s)",
                    (id , client_ip , client_port, ddos_status , get_timstamp()))
                break
        if client_id == -1: # not found client - setting new one
            insert_row(db, "clients",
                    "(client_id, ip, port, ddos_status, timestamp)",
                    "(%s, %s, %s, %s, %s)",
                    (len(all_clients)+1 , ip , port, False , get_timstamp()))

 

        if option == "STR":
            encrypted_data_size = client_socket.recv(256)
            data_size = int(eObj.decrypt_data(encrypted_data_size, server_private_key))
            all_transactions = get_all_rows(db, "transactions")
            if len(all_transactions) == 0:
                transaction_id = 1
            else:
                transaction_id = all_transactions[-1][0] + 1
            chunk_id = 0
            while data_size >= 245 :
                chunk_id = chunk_id + 1
                encrypted_data = client_socket.recv(256)
                data = eObj.decrypt_data(encrypted_data, server_private_key)
                insert_row(db, "transactions",
                              "(primary_trans_id , secondary_trans_id , client_id , timestamp , data_size , data )",
                              "(%s, %s, %s, %s, %s, %s)",
                              (transaction_id, chunk_id, client_id, get_timstamp(), 1024, data))
                data_size-=245
            if data_size > 0 :
                chunk_id = chunk_id +1
                encrypted_data = client_socket.recv(256)
                data = eObj.decrypt_data(encrypted_data, server_private_key)
                insert_row(db, "transactions",
                              "(primary_trans_id , secondary_trans_id , client_id , timestamp , data_size , data )",
                              "(%s, %s, %s, %s, %s, %s)",
                              (transaction_id, chunk_id, client_id, get_timstamp(), data_size, data))
            encrypted_transaction_id = eObj.encrypt_data(str(transaction_id), client_public_key)
            print("tr_id:", encrypted_transaction_id)
            client_socket.send(encrypted_transaction_id)
        elif option == "GET":
            all_clients = get_all_rows(db, "transactions")
            transaction_ids = []
            for (primary_trans_id,secondary_trans_id , id , timestamp , data_size , data ) in all_clients:
                    if client_id==id:
                        transaction_ids.append(primary_trans_id)
            encrypted_transaction_ids=eObj.encrypt_data(str(transaction_ids), client_public_key)
            client_socket.send(encrypted_transaction_ids)
            if not transaction_ids:
                print("")
            encrypted_data = client_socket.recv(256)
            data = eObj.decrypt_data(encrypted_data, server_private_key)
            selected_id=int(data)
            chunk_id=1
            data_size=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][4]
            while int(data_size) >= 245:
                data=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][5]
                data_size=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][4]
                print(data)
                encrypted_data = eObj.encrypt_data(data, client_public_key)
                print("encrypted data is:",encrypted_data)
                client_socket.send(encrypted_data)
                chunk_id+=1


            if data_size>0:
                data=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][5]
                print(data)
                encrypted_data = eObj.encrypt_data(data, client_public_key)
                client_socket.send(encrypted_data)
                data_size=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][4]
                chunk_id+=1




            


        else :
            print ("Unsupported option ", option)
    finally:
        # Close the connection after the transaction
        if ip in client_sockets and client_socket in client_sockets[ip]:
            client_sockets[ip].remove(client_socket)
            if not client_sockets[ip]:
                del client_sockets[ip]
            print(f"Removed socket for {ip}. Remaining: {len(client_sockets.get(ip, []))}")
        client_socket.close()


def initialize_db():
    mydb = init()
    create_database(mydb, "mysql")
    db = init_with_db("mysql")
    create_table(db, "clients",
                 "(client_id INT, ip VARCHAR(255), port INT, ddos_status BOOL, timestamp VARCHAR(255) )")
    create_table(db, "transactions",
                 "(primary_trans_id INT, secondary_trans_id INT, client_id INT, timestamp VARCHAR(255), data_size INT, data VARCHAR(1024))")
    print("created table")
    return db



class Server:
    def __init__(self):
        self.db =  initialize_db()
    def start_server(self,  host='127.0.0.1', port=5555):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print(f"Server listening on {host}:{port}...")
        
        while True:
            # Accept new client connections

            client_socket, client_address = server.accept()
            ip, _ = client_address

            if get_rows_from_table_with_value(self.db,"clients","ip",ip)[0][3]==True:
                print(f"This ip is blacklisted. Dropping connection from {ip}")

            total_connections = sum(len(sockets) for sockets in client_sockets.values())
            if total_connections >= 30:
                print(f"Global connection limit reached. Dropping connection from {ip}")
                client_socket.close()
                continue
            if ip in client_sockets and len(client_sockets[ip]) >= 15:
                update_value(self.db,"clients","ddos_status",True,"ip",ip)
                print(f"Too many connections from {ip}. Dropping.")
                client_socket.close()
                continue








            print(f"Connection from {client_address}")
            # Create a new thread to handle the client request
            client_handler = threading.Thread(target=handle_client, args=(self.db, client_socket, client_address))
            client_handler.start()

if __name__ == "__main__":
        




    eObj = Encryption()
    server_private_key = eObj.load_server_private_key()
    client_public_key = eObj.load_client_public_key()
    ui_starter=threading.Thread(target=start_ui, args=())
    ui_starter.start()
    s = Server()
    s.start_server()
    