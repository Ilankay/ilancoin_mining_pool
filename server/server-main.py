import sqlite3
import socket 
import threading

#gloabl constants
VALID_SIZE = 98
PKEY_LEN = 65 #length of public key in bytes

class CloseConn(Exception):
    """ an exception to throw in order to close a client connection"""
    pass

class DbApi:
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

class HandleClient:

    def add_client(self):
        print("client added")
        pass

    def add_work(self):
        print("work is added")
        pass

    def block_found(self):
        print("block is found!")
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
        self.operation_code = data[PKEY_LEN]
        self.hash = data[PKEY_LEN:]

        #should be moved into seperate method
        match(self.operation_code):
            case 0: return
            case 1: self.add_work()
            case 2: self.block_found()
            case 3: self.add_client()

def start_thread(conn, addr,db):
    """this starts the thread in order to handle a new client"""
    try:
        print(f"client connected from address: {addr}")
        client = HandleClient(conn,addr,db)
    except CloseConn:
        conn.shutdown()
        conn.close()

def init_server(host, port, db_path):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    #create db object
    db = DbApi(db_path)


    clients = 0
    threads = []
    # handle clients
    while True:
        conn, addr = server.accept()
        threads.append(threading.Thread(target=start_thread,args=(conn,addr,db)))
        threads[clients].start()
        clients+=1


if __name__ == "__main__":
    db_path = "work.db"
    HOST = "localhost"
    PORT = 1234
    init_server(HOST,PORT,db_path)