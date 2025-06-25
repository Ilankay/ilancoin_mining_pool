from exceptions import InvalidResponse,ExitProgram
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import struct
import zlib
import os

PK_SIZE = 2048
BUFF_SIZE = 1024
HEADER_SIZE = 9

def crc32_checksum(data: bytes) -> bytes:
    checksum = zlib.crc32(data) & 0xFFFFFFFF  # Ensure unsigned 32-bit integer
    return checksum.to_bytes(4, 'big')  # Convert to 4-byte bytes object

class EncryptedSocket:
    def __init__(self,port,address):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.settimeout(5)

        self.port = port
        self.address = address
        self.iv = None
        try:
            self.sock.connect((self.address,self.port))
        except ConnectionError:
            self.sock.shutdown(socket.SHUT_RDWR)
            raise ExitProgram

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir,"../other","enc_rsa_publickey")
        with open(file_path,'r') as keyfile:
            enc_rsa = RSA.import_key(keyfile.read())
        rsa_cipher = PKCS1_OAEP.new(enc_rsa)

        self.aes_key = get_random_bytes(16)
        enc_msg = rsa_cipher.encrypt(self.aes_key)
        length = struct.pack("!i",len(enc_msg))
        operation = struct.pack("!b",3)
        checksum = crc32_checksum(enc_msg)
        self.sock.sendall(length+operation+checksum+enc_msg)

    def send_message(self,data, operation):
        iv = get_random_bytes(16)
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)
        msg_padded = pad(data,16)
        ciphertext = aes_cipher.encrypt(msg_padded)
        
        msg = iv+ciphertext
        length = struct.pack("!I",len(msg))
        operation = struct.pack("!B",operation)
        checksum = crc32_checksum(msg)
        self.sock.sendall(length+operation+checksum+msg)
        # recieve response
        try:
            header = self.sock.recv(9)
            msg_len = struct.unpack("!I",header[:4])[0]
            msg_op = header[4]
            msg_checksum = header[5:]
            msg = self.sock.recv(msg_len)
            if crc32_checksum(msg) != msg_checksum:
                raise InvalidResponse
            iv_recv = msg[:16]
            aes_cipher = AES.new(self.aes_key,AES.MODE_CBC,iv=iv_recv)
        except TimeoutError:
            self.sock.shutdown(socket.SHUT_RDWR)
            raise ExitProgram

        return (msg_op,unpad(aes_cipher.decrypt(msg[16:]),16))





if __name__ == "__main__":
    es = EncryptedSocket(1234,"localhost")
    rsa = RSA.generate(PK_SIZE)
    print(rsa.public_key().export_key())
    #es.send_pk()

