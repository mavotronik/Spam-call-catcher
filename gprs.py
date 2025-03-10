import serial 
import time
import re
import yaml

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
    
config = load_config()


class GPRS:
    def __init__(self):
        self.port = config["serial"]["port"]
        self.baudrate = config["serial"]["baud_rate"]
        self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
        time.sleep(2)  # Wait for intialization
        self.ser.reset_input_buffer()

    def send_command(self, command, delay=1):
        """AT-command send & response receive"""
        self.ser.write((command + "\r\n").encode())
        time.sleep(delay)
        response = self.ser.read_all().decode(errors="ignore").strip()
        return response

    def initialize(self):
        """Check connection with GPRS"""
        init_response = self.ser.read_all().decode(errors="ignore")
        if "Serial init OK" in init_response:
            print("[INFO] Arduino is online!")

        response = self.send_command("AT")
        if "OK" in response:
            print("[SUCCESS] GPRS is online!")
            return True
        else:
            print("[ERROR] No response from GPRS module!")
            return False

    def test_echo(self):
        # Check and disable echo
        test_echo = self.send_command("AT")
        lines = test_echo.splitlines()
        if len(lines) >= 2 and lines[0] == "AT" and "OK" in lines:
            print("[INFO] Echo is enabled, disabling it...")
            self.send_command("ATE0")  # Turn off echo
            time.sleep(0.5)
            test_echo = self.send_command("AT")  # Check again
            if test_echo.startswith("AT"):
                print("[WARNING] Failed to disable echo!")
            else:
                print("[INFO] Echo disabled")
        else:
            print("[INFO] Echo is already disabled")

    def call_detect(self):
        # Turn on number recognition
        self.send_command("AT+CLIP=1")
        print("[INFO] Caller ID detection enabled")
        return True

    def get_signal_strength(self):
        """Request signal strength"""
        response = self.send_command("AT+CSQ")
        match = re.search(r"\+CSQ: (\d+),", response)
        if match:
            return int(match.group(1))
        return None

    def read_data(self):
        """Read data from module"""
        if self.ser.in_waiting > 0:
            response = self.ser.read_all().decode(errors="ignore").strip()
            return response
        return None

    def close(self):
        """TTY close"""
        self.ser.close()