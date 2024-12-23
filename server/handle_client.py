from exceptions import CloseConn,ClientExists
from db_api import DbApi

import random
#gloabl constants
VALID_SIZE = 98
PKEY_LEN = 65 #length of public key in bytes
VALID_SEND_SIZE = 67

class HandleClient:

    def create_msg(self,code:int,content:int):
        """this method creates a valid message to send to the client"""
        randbytes = lambda n:bytes(map(random.getrandbits,(8,)*n))
        server_pkey = randbytes(PKEY_LEN) #replace with server public key
        code = code.to_bytes(1,"little")
        content = content.to_bytes(1,"little")
        return server_pkey+code+content
    
    def add_client(self):
        """ this method will add a new client to the database"""
        try:
            self.db.add_client(self.pub_key)
            msg = self.create_msg(3,1)
            self.conn.sendall(msg)
            print("client added")
        except ClientExists:
            msg = self.create_msg(3,0)
            print("client already exists")
            self.conn.sendall(msg)

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

    def __init__(self, conn, addr, db:DbApi):
        self.db = db
        data = None
        while True:
            temp = conn.recv(VALID_SIZE*8)
            if not temp: break
            data = temp
        if not self.validate_data(data): 
            print("data is invalid")
            raise CloseConn
        print("data is valid")
        self.pub_key = data[:PKEY_LEN]
        self.operation_code = data[PKEY_LEN]
        self.hash = data[PKEY_LEN:]
        self.conn = conn
        #should be moved into seperate method
        match(self.operation_code):
            case 0: return
            case 1: self.add_work()
            case 2: self.block_found()
            case 3: self.add_client()
        raise CloseConn
