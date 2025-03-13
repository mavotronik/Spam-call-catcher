import time
import threading
import re
from gprs import GPRS

gprs = GPRS()

class CALLS:
    @staticmethod
    def answer_call():
        response = gprs.send_command("ATA")
        if "OK" in response:
            print("[INFO] Call answered")
            return True
        else:
            print("[ERROR] Failure")
        return False
    
    @staticmethod
    def end_call():
        response = gprs.send_command("ATH")
        if "OK" in response:
            print("[INFO] Call ended")
            return True
        else:
            print("[ERROR] Failure")
        return False    

    @staticmethod
    def monitor_calls():
        while True:
            data = gprs.read_data()
            if data:
                if "RING" in data:
                    print("[ALERT] Incoming call detected!")
                    return True
                if "+CLIP:" in data:
                    caller_number = data.split('"')[1]
                    print(f"[ALERT] Incoming call from: {caller_number}")
            time.sleep(2)

#threading.Thread(target=CALLS.monitor_calls, daemon=True).start()

