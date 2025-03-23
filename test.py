import struct
import time

def switch_endian(x:str):
    """switch_endian.

    :param x:
    :type x: str
    """
    out = ""
    for i,j in zip(x[::2][::-1],x[::-2]):
        out += i+j
    return out       


timestamp = str(hex(struct.unpack('>I',struct.pack('<I',int(time.time())))[0]))[2:]
timestamp_hex = hex(int(time.time()))
original_len = len(timestamp)
while True:
    if len(timestamp) != original_len:
        print(len(timestamp_hex),len(timestamp),timestamp)
    timestamp = str(hex(struct.unpack('>I',struct.pack('<I',int(time.time())))[0]))[2:]
    timestamp_hex = switch_endian(hex(int(time.time()))[2:])

