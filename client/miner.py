import time
import random

class Miner:
    def __init__(self,pkey):
        self.randbits = lambda n:bytes(map(random.getrandbits,(8,)*n))
        self.pkey = pkey
    def generateHash(self,size):
        time.sleep(10)
        return self.randbits(size)
