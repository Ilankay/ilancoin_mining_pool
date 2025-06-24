from exceptions import ExitProgram, InvalidAddr
import json
from bitpyminer import Miner
from server_conn import ServerConn
import time
from multiprocessing import Process, Queue, Event
import tkinter as tk
import threading
import time
from bech32 import bech32_decode

def server_communication(ilc_addr,server_connection,send_q,param_q,run,log):
    while True:
        data = send_q.get()
        identity = data[0]
        message = data[1:]

        if identity:
            print("block submitted")
            log_entry = f"Log entry: work submitted"
            log.insert(tk.END,log_entry)
            log.see(tk.END)
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
            log_entry = f"Log entry: work submitted"
            log.insert(tk.END,log_entry)
            log.see(tk.END)
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

def get_reward(ilc_address,output_div):
    for addr,amnt in output_div:
        if ilc_address == addr:
            return int(amnt,16)/100_000_000

def start_mining(ilc_address,cores,log,reward_val,run,param_q):
    server_connection = ServerConn()
    params = server_connection.recieve_mining_info(ilc_address)
    reward = get_reward(ilc_address,json.loads(params["output_div"]))
    reward_val.set(f"Current reward: {reward}")
    send_q = Queue()
    can_start = Event()

    processes = []

    send_thread =threading.Thread(target=server_communication,args=(ilc_address,server_connection,send_q,param_q,run,log))
    send_thread.start()

    for i in range(cores):
        p = Process(target=mine_process,args=(params,send_q,can_start,i))
        p.start()
        processes.append(p)
    print("miners active")
    log_entry = f"Log entry: miners active"
    log.insert(tk.END,log_entry)
    log.see(tk.END)

    can_start.set()

    while run.is_set():
        can_start.clear()
        new_params = param_q.get()
        reward = get_reward(ilc_address,json.loads(new_params["output_div"]))
        print(reward)
        reward_val.set(f"Current reward: {reward}")

        if not run.is_set(): break
        for p in processes:
            p.terminate()
            p.join()
        log_entry = f"Log entry: mining stopped\n"
        log.insert(tk.END,log_entry)
        processes = []
        for i in range(cores):
            p = Process(target=mine_process,args=(new_params,send_q,can_start,i))
            p.start()
            time.sleep(1.5)
            processes.append(p)
        print("miners active")
        log_entry = f"Log entry: miners active\n"
        log.insert(tk.END,log_entry)
        log.see(tk.END)
        can_start.set()

    for p in processes:
        p.terminate()
        p.join()
    processes = []
    print("mining stopped")



def start_logging():
    """Starts the logging process in a background thread."""
    address = address_entry.get()
    cores = core_slider.get()
    log_box.see(tk.END)  # Auto-scroll to latest log
    
    try:
        bech32_decode(address)
    except InvalidAddr:
        log_box.insert(tk.END, "❌ Invalid address! Please enter a valid BTC address.\n")
        log_box.see(tk.END)
        show_log_screen()
        return           
    show_log_screen()

    log_box.insert(tk.END, f"Starting process with address: {address} and {cores} cores\n")
    log_box.see(tk.END)  # Auto-scroll to latest log

    # Start the background worker thread
    global run
    global param_q
    run.set()
    thread = threading.Thread(target=start_mining, daemon=True,args=(address,cores,log_box,reward_value,run,param_q))
    thread.start()

def show_log_screen():
    """Switch to the log screen."""
    start_frame.pack_forget()
    log_frame.pack()

def show_start_screen():
    """Switch back to the start screen and stop logging."""
    global run
    run.clear()  # Stop the background thread
    log_frame.pack_forget()
    start_frame.pack()

# GUI Setup
root = tk.Tk()
root.title("ilancoin mining pool")
root.geometry("400x300")

run  = Event()
param_q = Queue()
# Start Screen
start_frame = tk.Frame(root)
start_frame.pack()

tk.Label(start_frame, text="Enter Address:").pack()
address_entry = tk.Entry(start_frame)
address_entry.pack()

tk.Label(start_frame, text="Select Cores:").pack()
core_slider = tk.Scale(start_frame, from_=1, to=12, orient=tk.HORIZONTAL)  
core_slider.pack()

start_button = tk.Button(start_frame, text="Start", command=start_logging)
start_button.pack()

# Log Screen
log_frame = tk.Frame(root)

reward_value = tk.StringVar()
reward_value.set("Current Reward: 0.0000 BTC")
reward_label = tk.Label(log_frame, textvariable=reward_value)
reward_label.pack()

log_box = tk.Text(log_frame, height=10, width=45)
log_box.pack()

back_button = tk.Button(log_frame, text="Back", command=show_start_screen)
back_button.pack()

def on_closing():
    global run
    global param_q
    param_q.put(json.dumps({}))
    run.clear()
    print("goodbye")
    root.destroy()
root.protocol("WM_DELETE_WINDOW",on_closing)
root.mainloop()

