import datetime
import os
from encryption_lib import Encryption

'''
eObj = Encryption()
server_public_key = encryption.load_server_public_key()
client_private_key = encryption.load_client_private_key()
'''
def get_timstamp():
    current_datetime = datetime.datetime.now()
    result = current_datetime.timestamp()
    return str(result)

       
# get picture and save to path
def get_picture_and_save_to_path(mysocket, picture_path):

    size = int(mysocket.recv(1024).decode())
    
    # open and write picture
    with open(picture_path, mode='wb') as file: # b is important -> binary
        total = 0
        # get "chunks"
        while total + 1024 < size:
            chunk = mysocket.recv(1024)
            file.write(chunk)
            total = total + 1024
        # get "tail"
        if (total < size):
            data = mysocket.recv(size - total) 
            file.write(data)


def get_size_of_pic(pic_path) :
    file_stats = os.stat(pic_path)
    return file_stats.st_size        


# send picture 
def send_string_file(mysocket, file_path, eObj, server_public_key, client_priv_key):
    # send size of picture
    size = get_size_of_pic(file_path)
    encrypted_size=eObj.encrypt_data(str(size), server_public_key)
    mysocket.send(encrypted_size)
    
    # open and read picture
    with open(file_path, 'rb') as file:
        total = 0
        # send "chunks"b
        while total + 245 < size:
            chunk = file.read(245)
            enc_chunk = eObj.encrypt_data((chunk).decode('latin1'), server_public_key)
            mysocket.send(enc_chunk)
            total = total + 245
        # send "tail"
        if (total < size):
            data = file.read(245)
            enc_chunk = eObj.encrypt_data((data).decode('latin1'), server_public_key)
            mysocket.send(enc_chunk)
