import sqlite3
import socket 
import threading

class CloseConn(Exception):
    pass

def handle_client(conn, addr):
   data = None
   while True:
       data = conn.recv(1024)
       conn.sendall(data)
       if data is None: break
    
    
def init_server(host, port):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    clients = 0
    threads = []

    while True:
        conn, addr = server.accept()
        threads.append(threading.Thread(target=handle_client,args=(conn,addr)))
        threads[clients].start()
        clients+=1
if __name__ == "__main__":
    HOST = "localhost"
    PORT = 1234
    init_server(HOST,PORT)