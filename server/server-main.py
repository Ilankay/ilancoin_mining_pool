import sqlite3
import socket 
import threading

class CloseConn(Exception):
    pass

def add_client(pub_key):
    pass

def add_work(pub_key,hash):
    pass

def block_found(pub_key,hash):
    pass

def handle_client(conn, addr):
    data = None
    while True:
       data = conn.recv(4354)
       if data is None: break
    pub_key = data[:512]
    operation_code = data[512]>>6 
    hash = (data[512:]<<6)>>6
    match(operation_code):
        case 0: return
        case 1: add_work(pub_key,hash)
        case 2: block_found(pub_key,hash)
        case 3: add_client(pub_key)
        
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