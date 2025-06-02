import threading
import os

def run_client():
    os.system('C:\\Users\\IMOE001\\AppData\\Local\\Programs\\Python\\Python313\\python.exe c:\\Users\\IMOE001\\cyber\\cyber\\moo_client.py')

threads = []

for i in range(100):
    t = threading.Thread(target=run_client)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
