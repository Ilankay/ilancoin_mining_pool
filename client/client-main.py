import socket 
import random
from miner import Miner

randbytes = lambda n:bytes(map(random.getrandbits,(8,)*n))

def send_data(operation_code):
    addr = randbytes(20)
    hash = randbytes(32)
    msg = addr+bytes(operation_code.to_bytes(1,"little"))+hash
    print(len(msg))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg)

if __name__ == "__main__":

    HOST = "localhost"
    PORT = 1234
    
    send_data(3)