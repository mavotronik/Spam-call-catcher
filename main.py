import serial
import time
import threading
import re

# Serial port settings
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

# Send and recieve commands function
def send_at_command(ser, command, delay=1):
    ser.write((command + "\r\n").encode())  # Send
    time.sleep(delay)
    response = ser.read_all().decode(errors="ignore")  # Parce input
    return response.strip()

def monitor_signal_strengh(ser):
    # Request for signal strength every 60 seconds
    while True:
        response = send_at_command(ser, "AT+CSQ")
        print("[INFO] Signal:", response)
        time.sleep(60)

def wait_for_incomig_call(ser):
    while True:
        while True:
            if ser.in_waiting > 0:  # Check if there is new data
                response = ser.read_all().decode(errors="ignore").strip()
            if "RING" in response:
                print("[ALERT] Incoming call detected!")
            match = re.search(r'\+CLIP: "(\d+)"', response)
            if match:
                caller_number = match.group(1)
                print(f"[ALERT] Incoming call from: {caller_number}")
            time.sleep(2)  # Check every 2 seconds


# Open TTY
with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
    time.sleep(2)  # Wait for initialization
    ser.reset_input_buffer()  # Clear input buffer

    # Check connection with GPRS module
    response = send_at_command(ser, "AT")
    if "OK" in response:
        print("[SUCCESS] GPRS is online!")
    else:
        print("[ERROR] No response from GPRS module!")
        exit(1)

    # Check if echo is enabled by sending "AT"
    test_echo = send_at_command(ser, "AT")
    lines = test_echo.splitlines()

    if len(lines) >= 2 and lines[0] == "AT" and "OK" in lines:
        print("[INFO] Echo is enabled, disabling it now...")
        send_at_command(ser, "ATE0")  # Try to disable echo
        time.sleep(0.5)
        test_echo = send_at_command(ser, "AT")  # Check again
        if test_echo.startswith("AT"):
            print("[WARNING] Failed to disable echo!")
        else:
            print("[INFO] Echo disabled")
    else:
        print("[INFO] Echo is already disabled")

    # Request for current operator
    response = send_at_command(ser, "AT+COPS?")
    print("[INFO] Operator:", response)

   # Enable caller ID notification
    send_at_command(ser, "AT+CLIP=1")
    print("[INFO] Caller ID detection enabled") 

    signal_thread = threading.Thread(target=monitor_signal_strengh, args=(ser,))
    signal_thread.daemon = True
    signal_thread.start()

    signal_thread = threading.Thread(target=wait_for_incomig_call, args=(ser,))
    signal_thread.daemon = True
    signal_thread.start()
 

    while True:
        time.sleep(2)