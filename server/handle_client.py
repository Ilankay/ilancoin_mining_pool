from exceptions import CloseConn,ClientExists
from db_api import DbApi

import random
#gloabl constants
VALID_SIZE = 53
WADDR_LEN = 20 #length of wallet address in bytes
VALID_SEND_SIZE = 22

class HandleClient:

    def create_msg(self,code:int,content:int):
        """this method creates a valid message to send to the client"""
        randbytes = lambda n:bytes(map(random.getrandbits,(8,)*n))
        server_waddr = randbytes(WADDR_LEN) #replace with server wallet address
        code_bytes = code.to_bytes(1,"little")
        content_bytes = content.to_bytes(1,"little")
        return server_waddr+code_bytes+content_bytes
    
    def add_client(self):
        """ this method will add a new client to the database"""
        try:
            self.db.add_client(self.wallet_addr)
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
    
    def validate_data(self,data)->bool:
        """the method returns true if data is valid and false if data is invalid"""

        if(len(data)==VALID_SIZE): #add logic for checking if the wallet address is valid or not 
            return True 
        return False
    
    def receive_data(self)->bytes:
        data = b''
        while True:
            temp = self.conn.recv(VALID_SIZE*8)
            if not temp: break
            data = temp
        return data
        
    
    def __init__(self, conn, addr, db:DbApi):
        self.db = db
        self.conn = conn
        
        data = self.receive_data()
       
        if not self.validate_data(data): 
            print("data is invalid")
            raise CloseConn
        print("data is valid")
        self.wallet_addr = int.from_bytes(data[:WADDR_LEN])
        self.operation_code = data[WADDR_LEN]
        self.hash = int.from_bytes(data[WADDR_LEN:])
        #should be moved into seperate method
        match(self.operation_code):
            case 0: return
            case 1: self.add_work()
            case 2: self.block_found()
            case 3: self.add_client()
        raise CloseConn
