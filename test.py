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

print(f"{1235:016x}")
