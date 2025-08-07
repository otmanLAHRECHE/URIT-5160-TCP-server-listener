import socket

HOST = "127.0.0.1"
PORT = 5000

hl7_message = "\x0b" + """MSH|^~\\&|URIT|UT-5160|LIS|PC|202508051230||ORU^R01|1234|P|2.3.1
PID|1||12345||DOE^JOHN
OBR|1||12345|Complete Blood Count
OBX|1|NM|HEMATOCRITE||42.1|%|36-48|N|F
OBX|2|NM|HEMOGLOBINE||14.2|g/dL|13-17|N|F
OBX|3|NM|GLOBULES ROUGES||4.8|M/µL|4.5-5.5|N|F
OBX|4|NM|TAUX DE PLAQUETTES||275|K/µL|150-450|N|F
OBX|5|NM|GLOBULES BLANCS||6.2|K/µL|4.0-10.0|N|F
OBX|6|NM|MXD||7.0|%|3-10|N|F
OBX|7|NM|CRP||5.2|mg/L|0-10|N|F
""" + "\x1c\r"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(hl7_message.encode('utf-8'))
    print("HL7 test message sent.")
