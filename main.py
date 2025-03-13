import time
import threading
import re
import yaml
from gprs import GPRS
from calls import CALLS

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

whitelist = config["call_settings"]["whitelist_path"]
blacklist = config["call_settings"]["blacklist_path"]
call_mode = config["call_settings"]["mode"]

gprs = GPRS()
calls = CALLS()

gprs.initialize()
gprs.test_echo()
gprs.call_detect()

def monitor_signal():
    while True:
        signal = gprs.get_signal_strength()
        if signal is not None:
            print(f"[INFO] Signal strength: {signal}")
            time.sleep(10)

def monitor_calls():
    while True:
        data = gprs.read_data()
        if data:
            if "RING" in data:
                print("[ALERT] Incoming call detected!")
            if "+CLIP:" in data:
                caller_number = data.split('"')[1]
                print(f"[ALERT] Incoming call from: {caller_number}")
                if should_answer(caller_number, call_mode):
                    if calls.answer_call():
                        print("[INFO] Call successfully answered")
                        time.sleep(10)
                        calls.end_call()
                else:
                    print("[ERROR] Failed to answer call")
        time.sleep(2)

def should_answer(caller_number, call_mode):
    if call_mode == "all":
        if caller_number in blacklist:
            print(f"[INFO] Number {caller_number} in blacklist, ignore.")
            return False
        else:
            print(f"[INFO] Number {caller_number} not in blacklist, answer.")
            return True
    
    if call_mode == "whitelist":
        if caller_number in whitelist:
            print(f"[INFO] Number {caller_number} in whitelist, answer.")
            return True
        else: 
            print(f"[INFO] Number {caller_number} not in whitelist, ignore.")
            return False
        
    if call_mode == "ignore_all":
        print(f"[INFO] ALL numbers should be IGNORE!")
        return False




threading.Thread(target=monitor_signal, daemon=True).start()
threading.Thread(target=monitor_calls, daemon=True).start()

# Основной цикл
while True:

    time.sleep(1)