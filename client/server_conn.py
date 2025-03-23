class ServerConn:
    def __init__(self):
        pass
    def recieve_mining_info(self):
        params = {
            "height":"05",
            "version":"20000000",
            "bits":"1d00ffff",
            "prev block":"00000000f616a555f37553fd69d9ed59315ad48c3894b75e30cc606f84d42ea6",
            "transactions":[]
        }
        return params
    def submit_work(self,block_header):
        print(block_header)
    def submit_block(self,block):
        print(block)
        
