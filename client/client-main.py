import socket 
from exceptions import ExitProgram
import json
import threading
from bitpyminer import Miner
from server_conn import ServerConn
import struct
import time
from multiprocessing import Process, Queue, Event
import signal
import sys

def base58_decode(base58_addr):
    return base58_addr

def server_communication(ilc_addr,server_connection,send_q,param_q,run):
    while True:
        data = send_q.get()
        identity = data[0]
        message = data[1:]

        if identity:
            print("block submitted")
            try:
                new_params = server_connection.submit_block(ilc_addr,message)
            except ExitProgram:
                run.clear()
                param_q.put(json.dumps({}))
                return
            if len(new_params.keys())!=0:
                param_q.put(new_params)

        if not identity: 
            print("work submitted")
            try:
                new_params = server_connection.submit_work(ilc_addr,message)
            except ExitProgram:
                run.clear()
                param_q.put(json.dumps({}))
                return
            if len(new_params.keys())!=0:
                param_q.put(new_params)


def mine_process(mining_params,send_q,can_start,offset):
    miner = Miner(stdout=False,q_flag=True,send_q=send_q)
    can_start.wait()
    miner.mine(json.loads(mining_params["output_div"]),
                                         mining_params["height"],
                                         mining_params["version"],
                                         mining_params["prev block"],
                                         mining_params["bits"],time_offset=offset)

def start_mining(ilc_address,cores):
    server_connection = ServerConn()
    params = server_connection.recieve_mining_info(ilc_address)
    param_q = Queue()
    send_q = Queue()
    can_start = Event()
    run  = Event()
    run.set()
    processes = []

    send_thread =threading.Thread(target=server_communication,args=(ilc_address,server_connection,send_q,param_q,run))
    send_thread.start()

    for i in range(cores):
        p = Process(target=mine_process,args=(params,send_q,can_start,i))
        p.start()
        processes.append(p)
    print("miners active")
    can_start.set()
    time.sleep(1)

    while run.is_set():
        can_start.clear()
        new_params = param_q.get()
        if not run.is_set(): break
        for p in processes:
            p.terminate()
            p.join()
        processes = []
        for i in range(cores):
            p = Process(target=mine_process,args=(new_params,send_q,can_start,i))
            p.start()
            time.sleep(1.5)
            processes.append(p)
        print("miners active")
        can_start.set()
        new_params = param_q.get()

    for p in processes:
        p.terminate()
        p.join()
    processes = []



if __name__ == "__main__":
    base58_addr = input("hello welcome to the pool miner, please enter your ilancoin address in base58 format")
    proc_cnt = int(input("please enter the amount of cores you want to use:"))
    addr = base58_decode(base58_addr)
    test_addr = "0638a075aeb98f5d1404fc69dcaed3c4e71ce611"

    start_mining(test_addr,proc_cnt)

