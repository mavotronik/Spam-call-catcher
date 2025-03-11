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
            time.sleep(60)

def monitor_calls():
    while True:
        data = gprs.read_data()
        if data:
            if "RING" in data:
                print("[ALERT] Incoming call detected!")
                if calls.answer_call():
                    print("[INFO] Call successfully answered")
                    time.sleep(10)
                    calls.end_call()
                else:
                    print("[ERROR] Failed to answer call")
            if "+CLIP:" in data:
                caller_number = data.split('"')[1]
                print(f"[ALERT] Incoming call from: {caller_number}")
        time.sleep(2)

threading.Thread(target=monitor_signal, daemon=True).start()
threading.Thread(target=monitor_calls, daemon=True).start()

# Основной цикл
while True:

    time.sleep(1)