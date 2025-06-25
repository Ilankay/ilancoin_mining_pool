from encrypted_socket import EncryptedSocket
from exceptions import ExitProgram
import json
PORT = 1234
ADDR = "localhost"
PK_SIZE = 2048

class ServerConn:
    def __init__(self):
        self.es = EncryptedSocket(PORT,ADDR) 


    def recieve_mining_info(self,ilc_address):
        test_params = {
            "height":"05",
            "version":"20000000",
            "bits":"1d00ffff",
            "prev block":"00000000f616a555f37553fd69d9ed59315ad48c3894b75e30cc606f84d42ea6",
            "transactions":[]
        }
        params = self.es.send_message(ilc_address.encode(),0)[1]
        return json.loads(params.decode())

    def submit_work(self,ilc_address,block_header)->dict:
        return_op,return_val = self.es.send_message(ilc_address.encode()+block_header,1)
        if return_op == 1:
            print("work submitted succsessfully")
            return json.loads(return_val)
        elif return_op == 4:
            raise ExitProgram
        else:
            print(f"error: {return_val}")
            return {}
        
    def submit_block(self,ilc_address,block):
        return_op,return_val = self.es.send_message(ilc_address.encode()+block,2)
        if return_op == 1:
            print("block submitted succsessfully")
            return json.loads(return_val)
        elif return_op == 4:
            raise ExitProgram
        else:
            print(f"error: {return_val}")
            return {}
               
 
