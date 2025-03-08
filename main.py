import serial
import time

# Serial port settings
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

# Send and recieve commands function
def send_at_command(ser, command, delay=1):
    ser.write((command + "\r\n").encode())  # Send
    time.sleep(delay)
    response = ser.read_all().decode(errors="ignore")  # Parce input
    return response.strip()

# Open TTY
with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
    time.sleep(2)  # Wait for initialisation
    ser.reset_input_buffer()  # Clear input buffer

    # Check connectio with GPRS module
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

    # Request for signal strength
    response = send_at_command(ser, "AT+CSQ")
    print("[INFO] Signal:", response)
