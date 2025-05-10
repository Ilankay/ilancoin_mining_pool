import enum
from exceptions import CloseConn,ClientExists
from encrypted_socket import EncryptedSocket
from db_api import DbApi
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
from bitpyminer import BlockHeader,Output,CoinbaseTransaction
import struct

def encode_compactsize(i):
    if i <= 252:
        return f"{i:02x}"
    elif i <= 65535:
        return "fd" + struct.pack("<H", i).hex()
    elif i <= 4294967295:
        return "fe" + struct.pack("<I", i).hex()
    elif i <= 18446744073709551615:
        return "ff" + struct.pack("<Q", i).hex()


class HandleClient:

    def __init__(self, conn, addr, db:DbApi):
        self.db = db
        self.conn = conn
        self.es = EncryptedSocket(conn,addr)
        self.params = self.get_mining_params()
        while True:
            operation, message = self.es.recieve_message()
            match operation:
                case 0: self.send_mining_params(message),
                case 1: self.verify_work(message),
                case 2: self.verify_block(message),
                case 4: break

        raise CloseConn

    def get_client_outputs(self,amnt):
        sum = 0
        array_work = json.loads(self.db.list_addresses_work())
        for addr, work in array_work:
            sum += work
        for index,i in enumerate(array_work):
            array_work[index][1] = f"{int(i[1]/sum * amnt):016x}"
        return array_work
    
    def get_mining_params(self):
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%("admin", "admin"))
        template = rpc_connection.getblocktemplate({"rules":["segwit"]})
        params = {
            "height":"0"+str(hex(template["height"]))[2:],
            "version":str(hex(template["version"]))[2:],
            "bits":template["bits"],
            "prev block":template["previousblockhash"],
            "transactions":template["transactions"],
            "output_div":json.dumps(self.get_client_outputs(template["coinbasevalue"]))
        }
        return params

    def send_mining_params(self,msg):
        waddr = msg.decode()
        try:
            self.db.add_client(waddr)
        except ClientExists:
            pass

        params = self.get_mining_params()
        self.params = params
        self.es.send_message(json.dumps(params).encode(),2)

    def construct_coinbasetx(self,output_div,height):
        outputs = []
        for address,amnt in output_div:
            outputs.append(Output(amnt=amnt,address=address))
        outputs.append(Output(amnt="0000000000000000",script_type = "commitment"))
        cnt = encode_compactsize(len(outputs))
        return CoinbaseTransaction(height,output_count=str(cnt),outputs=outputs)

    def verify_work(self,msg):
        msg = msg.decode()
        params = self.params
        coinbasetx = self.construct_coinbasetx(output_div=json.loads(params["output_div"]),height=params["height"])
        block_header = BlockHeader(params["version"],
                                   params["prev block"],
                                   params["bits"],
                                   txns=[coinbasetx]+params["transactions"],
                                   timestamp=msg[176:184])
        waddr = msg[:40]

        bits = params["bits"]
        exponent = int(bits[0:2],16)
        coefficient = int(bits[2:],16)
        target = coefficient * 2**(8 * (exponent - 3))
        small_target = target*16

        int_hash = int(block_header.calc_hash(msg[-8:]),16)

        if int_hash <= small_target:
            try:
                self.db.add_client(waddr)
            except ClientExists:
                pass
            self.db.add_work(waddr)
            self.params = self.get_mining_params()
            self.es.send_message(json.dumps(self.params).encode(),1)
        else:
            self.es.send_message((b'high hash'),0)

        
    def verify_block(self,msg):
        msg = msg.decode()
        waddr = msg[:40]
        block = msg[40:]

        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%("admin", "admin"))
        error = rpc_connection.submitblock(block)
        if len(error)==0:
            try:
                self.db.add_client(waddr)
            except ClientExists:
                pass
            self.db.add_work(waddr)
            self.params = self.get_mining_params()
            self.es.send_message(json.dumps(self.params).encode(),1)
        else:
            self.es.send_message(error.encode(),0)



if __name__ == "__main__":
    db = DbApi("work.db")
    db.list_addresses_work()
    sum = 0
    amnt = 50_000_000
    array_work = json.loads(db.list_addresses_work())
    for addr, work in array_work:
        sum += work
    for index,i in enumerate(array_work):
        array_work[index][1] = str(hex(int((i[1]/sum) * amnt)))[2:]
    print(array_work)
