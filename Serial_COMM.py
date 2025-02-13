import serial.tools.list_ports
import serial

import socket
import select

class Serial:
    def __init__(self, type):
        self.buffer = ""
        if type == "BT":
            self.type = type
            print("Bluetooth selected")

        else:
            self.type = "RS232"
            print("RS232 selected")
        self.connected = False

    def ClearBuffer(self):
        self.buffer = ""

    def message_set(self, sign_start, sign_stop):
        self.sign_start = str(sign_start)
        self.sign_stop  = str(sign_stop)

    def init_RS232(self, port, baudrate):
        self.port_RS = port
        self.baudrate = baudrate

    def init_Bluetooth(self, MAC_adress, port):
        self.port_BT = port
        self.MAC_BT = MAC_adress

    def connect(self):
        if self.type == "RS232":
            self.ser = serial.Serial(
                port = self.port_RS,
                baudrate = self.baudrate,
                timeout=0,)
            print(f"Connect to {self.ser.port} with {self.ser.baudrate}")
            return True
        else:
            self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            try:
                # Verbindung herstellen
                print(f"Connecting to {self.MAC_BT} on port {self.port_BT}...")
                self.sock.connect((self.MAC_BT, self.port_BT))
                print("Connected successfully!")
                return True
            except Exception as e:
                print(f"An error occurred: {e}")
                return False

    def RS_get_available_ports(self):
        ports = serial.tools.list_ports.comports()  # Alle Ports abfragen
        filtered_ports = []
        for port in ports:
            portname = str(port)
            comPortVar = str(portname.split(' ')[0])
            print(comPortVar, portname, ports)
            filtered_ports.append(comPortVar)
        return filtered_ports

    def send_message(self, message):
        message = self.sign_start + str(message) + self.sign_stop
        if self.type == "RS232":
            try:
                self.ser.write(message.encode('utf-8'))
            except KeyboardInterrupt:
                print("ERROR *******************")
        else:
            self.sock.send(message.encode())

    def read_port(self):
        # print("Lese Daten")
        if self.type == "RS232":
            # print("RS")
            if self.ser.in_waiting > 0:  # Überprüfen, ob Daten im Puffer sind
                data = self.ser.read(self.ser.in_waiting)  # Alle verfügbaren Zeichen lesen
                # print(data)
                self.buffer += str(data)
                return True
        else:
            ready_to_read, _, _ = select.select([self.sock], [], [], 0.5)
            if ready_to_read:
                data = self.sock.recv(1024)
                if data:
                    self.buffer += data.decode('utf-8')
                    return True
        return False

    def analyze_message(self):
        # print("BUFFER:",self.buffer)
        if self.sign_start in self.buffer and self.sign_stop in self.buffer:
            # String zwischen Start- und Stop-Zeichen extrahieren
            start_index = self.buffer.index(self.sign_start)
            try:
                stop_index = self.buffer.index(self.sign_stop, start_index)  # Nach dem Startzeichen suchen
                if start_index < stop_index:
                    full_message = self.buffer[start_index + len(self.sign_start):stop_index]  # Nachricht inklusive Stop-Zeichen
                    # Den verarbeiteten Teil aus dem Puffer entfernen
                    self.buffer = self.buffer[stop_index + len(self.sign_stop):]
                    return full_message
            except Exception:
                return False
                # duration = time.time() - start_time
                #print(f"{duration:.3f} --> {full_message}")
        return False

    def Close(self):
        if self.type == "RS232":
            self.ser.close()
        else:
            self.sock.close()
