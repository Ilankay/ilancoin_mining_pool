import socket 
import random
import threading
from bitpyminer import Miner
from server_conn import ServerConn
import struct

def base58_decode(base58_addr):
    return base58_addr

def server_communication(server_connection):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(("localhost",1111))
    server.listen()
    while True:
        conn, addr = server.accept()
        length = conn.recv(4)
        identity = conn.recv(1)
        if not length:  
            break
        length = struct.unpack("!I",length)[0]
        identity = struct.unpack("!B",identity)[0]
        message = conn.recv(length)
        if identity:
            server_connection.submit_block(message)
        if not identity: 
            server_connection.submit_work(message)
        

def mine_and_send(ilc_addr,server_connection,mining_params):
    miner = Miner(ilc_addr,stdout=False,out_socket={"port":1111,"address":"localhost"})
    mine_thread = threading.Thread(target=miner.mine,
                                   args=(mining_params["height"],
                                                     mining_params["version"],
                                                     mining_params["prev block"],
                                         mining_params["bits"]))

    send_thread =threading.Thread(target=server_communication,args=(server_connection,))
    send_thread.start()
    print("server connection started")
    mine_thread.start()
    print("mining thread started")
    
if __name__ == "__main__":
    base58_addr = input("hello welcome to the pool miner, please enter your ilancoin address in base58 format")
    addr = base58_decode(base58_addr)
    server_connection = ServerConn()
    test_addr = "0638a075aeb98f5d1404fc69dcaed3c4e71ce611"
    params = server_connection.recieve_mining_info()
    mine_and_send(test_addr,server_connection,params)

