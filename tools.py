import datetime
import os

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
def send_string_file(mysocket, file_path):
    # send size of picture
    size = get_size_of_pic(file_path)
    mysocket.send(str(size).encode())
    
    # open and read picture
    with open(file_path, 'r') as file:
        total = 0
        # send "chunks"b
        while total + 1024 < size:
            chunk = file.read(1024)
            mysocket.send(chunk.encode())
            total = total + 1024
        # send "tail"
        if (total < size):
            data = file.read(size - total)
            mysocket.send(data.encode())
