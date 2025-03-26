from os import wait
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import struct
import zlib
from exceptions import CloseConn
PK_SIZE = 2048
BUFF_SIZE = 1024
HEADER_SIZE = 9

def crc32_checksum(data: bytes) -> bytes:
    checksum = zlib.crc32(data) & 0xFFFFFFFF  # Ensure unsigned 32-bit integer
    return checksum.to_bytes(4, 'big')  # Convert to 4-byte bytes object

class InvalidResponse(Exception):
    pass

class EncryptedSocket:
    def __init__(self,socket,address):

        self.sock = socket
        self.address = address
        self.rsakey = None
        self.iv = None
        
        header = self.sock.recv(9)
        msg_len = struct.unpack("!I",header[:4])[0]
        msg_op = header[4]
        msg_checksum = header[5:]
        msg = self.sock.recv(msg_len)
        if crc32_checksum(msg) != msg_checksum or msg_op != 3:
            raise InvalidResponse

        enc_rsa = RSA.import_key(msg)
        rsa_cipher = PKCS1_OAEP.new(enc_rsa)
        
        self.aes_key = get_random_bytes(16)
        enc_msg = rsa_cipher.encrypt(self.aes_key)
        length = struct.pack("!I",len(enc_msg))
        operation = struct.pack("!B",3)
        checksum = crc32_checksum(enc_msg)
        self.sock.sendall(length+operation+checksum+enc_msg)


    def send_message(self,data, operation):
        iv = get_random_bytes(16)
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)
        print(data)
        msg_padded = pad(data,16)
        ciphertext = aes_cipher.encrypt(msg_padded)
        
        msg = iv+ciphertext
        length = struct.pack("!I",len(msg))
        operation = struct.pack("!B",operation)
        checksum = crc32_checksum(msg)
        self.sock.sendall(length+operation+checksum+msg)
        return

    def recieve_message(self):
        header = self.sock.recv(9)
        if len(header) == 0:
            raise CloseConn
        msg_len = struct.unpack("!I",header[:4])[0]
        msg_op = header[4]
        msg_checksum = header[5:]
        msg = self.sock.recv(msg_len)
        if len(msg) == 0:
            raise CloseConn
        if crc32_checksum(msg) != msg_checksum:
            raise InvalidResponse
        iv_recv = msg[:16]
        aes_cipher = AES.new(self.aes_key,AES.MODE_CBC,iv=iv_recv)

        return (msg_op,unpad(aes_cipher.decrypt(msg[16:]),16))




