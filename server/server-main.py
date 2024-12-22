import sqlite3
import socket 
import threading

#gloabl constants
VALID_SIZE = 4099
PKEY_LEN = 512 #length of public key in bytes

class CloseConn(Exception):
    """ an exception to throw in order to close a client connection"""
    pass

class db_api:
    def __init__(self, db_path:str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='work';"
            if cur.execute(query).fetchall() != "work":
                query = "CREATE TABLE work (id INTEGER, pkey TEXT, work INTEGER, PRIMARY KEY(id,pkey));"
                cur.execute(query)
            conn.commit()

    def add_client(self,pkey):
        pass

class handle_client:

    def add_client(self):
        pass

    def add_work(self):
        pass

    def block_found(self):
        pass
    def validate_data(se1f,data)->bool:
        """the method returns true if data is valid and false if data is invalid"""
        if(len(data)==VALID_SIZE): #add logic for checking if the public key is valid or not 
            return True 
        return False

    def __init__(self, conn, addr, db):
        self.db = db
        data = None
        while True:
            data = conn.recv(VALID_SIZE)
            if data is None: break
        if not self.validate_data(data): raise CloseConn
        self.pub_key = data[:PKEY_LEN]
        self.operation_code = data[PKEY_LEN]>>6 
        self.hash = (data[PKEY_LEN:]<<6)>>6

        #should be moved into seperate method
        match(self.operation_code):
            case 0: return
            case 1: self.add_work()
            case 2: self.block_found()
            case 3: self.add_client()

def start_thread(conn, addr):
    """this starts the thread in order to handle a new client"""
    try:
        client = handle_client(conn,addr)
    except CloseConn:
        conn.shutdown()
        conn.close()

def init_server(host, port, db_path):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    #create db object
    db = db_api(db_path)


    clients = 0
    threads = []
    # handle clients
    while True:
        conn, addr = server.accept()
        threads.append(threading.Thread(target=handle_client,args=(conn,addr,db)))
        threads[clients].start()
        clients+=1


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 1234
    init_server(HOST,PORT)