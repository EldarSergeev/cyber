import socket
import threading
import random
from db_tools import *    
from tools import *
from encryption_lib import Encryption











# Function to handle client communication
def handle_client(db, client_socket,client_address):
    try:
        # receive option STR/GET
        option = client_socket.recv(4).decode()
        (ip, port) = client_address
        all_clients = get_all_rows(db, "clients")
        # for now client is identified by ip only
        client_id = -1
        for (id , client_ip , client_port, ddos_status , timestamp ) in all_clients:
            if ip == client_ip: # found our client
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
            data_size = int(client_socket.recv(2).decode())
            all_transactions = get_all_rows(db, "transactions")
            if len(all_transactions) == 0:
                transaction_id = 1
            else:
                transaction_id = all_transactions[-1][0] + 1
            chunk_id = 0
            while data_size >= 1024 :
                chunk_id = chunk_id + 1
                data = client_socket.recv(1024).decode()
                insert_row(db, "transactions",
                              "(primary_trans_id , secondary_trans_id , client_id , timestamp , data_size , data )",
                              "(%s, %s, %s, %s, %s, %s)",
                              (transaction_id, chunk_id, client_id, get_timstamp(), 1024, data))
            if data_size > 0 :
                chunk_id = chunk_id +1
                data = client_socket.recv(data_size).decode()
                insert_row(db, "transactions",
                              "(primary_trans_id , secondary_trans_id , client_id , timestamp , data_size , data )",
                              "(%s, %s, %s, %s, %s, %s)",
                              (transaction_id, chunk_id, client_id, get_timstamp(), data_size, data))
            client_socket.send(str(transaction_id).encode())
            
        elif option == "GET":
            all_clients = get_all_rows(db, "transactions")
            transaction_ids = []
            for (primary_trans_id,secondary_trans_id , id , timestamp , data_size , data ) in all_clients:
                    if client_id==id:
                        transaction_ids.append(primary_trans_id)
            client_socket.send(str(transaction_ids).encode())
            if not transaction_ids:
                print("")
            selected_id=int(client_socket.recv(1024).decode())
            chunk_id=1
            data_size=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][4]
            while int(data_size) >= 1024:
                data=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][5]
                data_size=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][4]
                client_socket.send(data.encode())
                chunk_id+=1


            if data_size>0:
                data=get_rows_from_table_with_two_value(db,"transactions","secondary_trans_id",str(chunk_id),"primary_trans_id",str(selected_id))[0][5]
                client_socket.send(data.encode())
                chunk_id+=1




            


        else :
            print ("Unsupported option ", option)
    finally:
        # Close the connection after the transaction
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
            print(f"Connection from {client_address}")
            
            # Create a new thread to handle the client request
            client_handler = threading.Thread(target=handle_client, args=(self.db, client_socket, client_address))
            client_handler.start()

if __name__ == "__main__":
    s = Server()
    s.start_server()