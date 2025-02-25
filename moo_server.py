import socket
import threading
import random
from db_tools import *    
from tools import *



def id_stamp(mydb_db, client_socket,client_adress):
    if get_rows_from_table_with_two_value(mydb_db,"data_user","ip",client_adress[0],"port",client_adress[1]):
        if get_rows_from_table_with_two_value(mydb_db,"data_user","ip",client_adress[0],"port",client_adress[1])[3]==1:
            client_socket.send(("your banned from the server connection termenaited").encode('utf-8'))
        else:
            return get_rows_from_table_with_two_value(mydb_db,"data_user","ip",client_adress[0],"port",client_adress[1])[0]
    else:
        id=random.randint(1, 10000)
        while get_rows_from_table_with_value(mydb_db,"data_user","id",id):
            id=random.randint(1, 10000)

        insert_row(mydb_db, "data_user",
                 "(id, ip, port ,Isblacklisted ,Connections_per_day )",
                 "(%s, %s, %s, %s, %s )",
                 (id, client_adress[0], client_adress[1] ,0 ,1 ))
        return id 
        


#function to handle client reqests recives the client's socket and id
def handle_client_request(client_socket,client_id):



    #extracts the clients message from the socket
    #if the message doesnt equal to "request" it checks for errors and inserets the message and clients info into the transections data table
    if client_socket.recv().decode() !="STR":
        try:
            result = [c for c in client_socket.decode(1024) if c != ' ']
            if len(result)>5:
                raise Exception("your message is too long")
        except Exception as e:
            client_socket.send(f"Error in expression: {e}".encode('utf-8'))
        finally:
            client_socket.send(("enter the password for your message").encode('utf-8'))
            password=client_socket.recv(1024).decode('utf-8')
            insert_row(mydb_db, "transections",
                 "(src_id, timeset, password, is_succeded ,trans_id ,char_1 ,char_2 ,char_3, char_4 ,char_5 )",
                 "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                 (client_id, "", password, 0 ,0 ,result[0] ,result[1], result[2], result[3],result[4]  ))
    else:
        client_socket.send(("enter the password for your message").encode('utf-8'))
        password=client_socket.recv(1024).decode('utf-8')
        if get_rows_from_table_with_value(mydb_db,"transections","password",password):
            update_value(mydb_db,"transections","trans_id",client_id,"password",password)
            #need to add a function that stamps the time of transection and updates is
            update_value(mydb_db,"transections","is_succeded",1,"password",password)  
            chr1=get_rows_from_table_with_value(mydb_db,"transections","password",password)[5]
            chr2=get_rows_from_table_with_value(mydb_db,"transections","password",password)[6]
            chr3=get_rows_from_table_with_value(mydb_db,"transections","password",password)[7]
            chr4=get_rows_from_table_with_value(mydb_db,"transections","password",password)[8]
            chr5=get_rows_from_table_with_value(mydb_db,"transections","password",password)[9]
            message=chr1+chr2+chr3+chr4+chr5


            client_socket.send(message)
        else:
            client_socket.send(("wrong password try again").encode('utf-8'))










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
                insert_row(db, "transcations",
                              "(primary_trans_id , secondary_trans_id , client_id , timestamp , data_size , data )",
                              "(%s, %s, %s, %s, %s, %s)",
                              (transaction_id, chunk_id, client_id, get_timstamp(), 1024, data))
            if data_size > 0 :
                chunk_id = chunk_id +1
                data = client_socket.recv(data_size).decode()
                insert_row(db, "transcations",
                              "(primary_trans_id , secondary_trans_id , client_id , timestamp , data_size , data )",
                              "(%s, %s, %s, %s, %s, %s)",
                              (transaction_id, chunk_id, client_id, get_timstamp(), data_size, data))
            client_socket.send(str(transaction_id).encode())
            
        elif option == "GET":
            pass
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