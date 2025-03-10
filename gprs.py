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
        time.sleep(2)  # Ждем инициализации
        self.ser.reset_input_buffer()

    def send_command(self, command, delay=1):
        """Отправка AT-команды и получение ответа"""
        self.ser.write((command + "\r\n").encode())
        time.sleep(delay)
        response = self.ser.read_all().decode(errors="ignore").strip()
        return response

    def initialize(self):
        """Проверка соединения с GPRS-модулем"""
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
        # Проверяем и отключаем эхо
        test_echo = self.send_command("AT")
        lines = test_echo.splitlines()
        if len(lines) >= 2 and lines[0] == "AT" and "OK" in lines:
            print("[INFO] Echo is enabled, disabling it...")
            self.send_command("ATE0")  # Отключаем эхо
            time.sleep(0.5)
            test_echo = self.send_command("AT")  # Проверяем еще раз
            if test_echo.startswith("AT"):
                print("[WARNING] Failed to disable echo!")
            else:
                print("[INFO] Echo disabled")
        else:
            print("[INFO] Echo is already disabled")

    def call_detect(self):
        # Включаем определение номера звонящего
        self.send_command("AT+CLIP=1")
        print("[INFO] Caller ID detection enabled")
        return True

    def get_signal_strength(self):
        """Запрос уровня сигнала"""
        response = self.send_command("AT+CSQ")
        match = re.search(r"\+CSQ: (\d+),", response)
        if match:
            return int(match.group(1))  # Возвращаем уровень сигнала
        return None

    def read_data(self):
        """Чтение входящих данных от модуля"""
        if self.ser.in_waiting > 0:
            response = self.ser.read_all().decode(errors="ignore").strip()
            return response
        return None

    def close(self):
        """Закрытие соединения"""
        self.ser.close()