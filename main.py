import time
import threading
import re
import yaml
from gprs import GPRS

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

gprs = GPRS()

gprs.test_echo()
gprs.call_detect()

def monitor_signal():
    while True:
        signal = gprs.get_signal_strength()
        if signal is not None:
            print(f"[INFO] Signal strength: {signal}")