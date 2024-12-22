from exceptions import CloseConn

#gloabl constants
VALID_SIZE = 98
PKEY_LEN = 65 #length of public key in bytes


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
            print("test")
            data = conn.recv(VALID_SIZE*8)
            if not data: break
        if not self.validate_data(data): 
            print("data is invalid")
            raise CloseConn
        print("data is valid")
        self.pub_key = data[:PKEY_LEN]
        self.operation_code = data[PKEY_LEN]
        self.hash = data[PKEY_LEN:]

        #should be moved into seperate method
        match(self.operation_code):
            case 0: return
            case 1: self.add_work()
            case 2: self.block_found()
            case 3: self.add_client()
        raise CloseConn
