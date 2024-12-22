import socket 
import threading

from db_api import DbApi
from handle_client import HandleClient
from exceptions import CloseConn

#gloabl constants
VALID_SIZE = 98
PKEY_LEN = 65 #length of public key in bytes

class ClThread(threading.Thread):
    def __init__(self, conn, addr, db):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.db = db
    def run(self):
        try:
            print(f"client connected from address: {self.addr}")
            HandleClient(self.conn,self.addr,self.db)
        except CloseConn:
            print("the connection has closed")
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()

def init_server(host, port, db_path):
    """this function accepts the host port and db_path and starts the server """
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    
    #create db object
    db = DbApi(db_path)

    print("server is up")
    clients = 0
    threads = []
    # handle clients
    try:
        while True:
            conn, addr = server.accept()
            threads.append(ClThread(conn,addr,db))
            threads[clients].start()
            clients+=1
    except KeyboardInterrupt:
        for thread in threads:
            thread.join()
        server.shutdown(socket.SHUT_RDWR)
        server.close()
        print("\nserver closed")
    


if __name__ == "__main__":
    db_path = "server/work.db"
    HOST = "localhost"
    PORT = 1234
    init_server(HOST,PORT,db_path)


