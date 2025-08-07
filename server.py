import socket
import json
import re

HOST = "0.0.0.0"
PORT = 5000

def normalize_segments(raw):
    # HL7 segments are usually separated by \r but devices sometimes send \n or \r\n.
    # Convert any combination to single \r for consistent splitting.
    return re.sub(r'\r\n|\n|\r', '\r', raw)

def parse_hl7_message(raw):
    results = {}
    normalized = normalize_segments(raw).strip()
    segments = normalized.split('\r')
    for seg in segments:
        if not seg:
            continue
        parts = seg.split('|')
        if parts[0] == 'OBX':
            try:
                identifier_field = parts[3]  # e.g. "HEMATOCRITE"
                value_field = parts[5]       # e.g. "42.1"
                test_name = identifier_field.split('^')[0].strip()
                test_value = value_field.strip()
                if test_name:
                    results[test_name] = test_value
            except IndexError:
                continue
    return results

def handle_data(data):
    print("📦 Raw HL7 Message Received:")
    print(repr(data))

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🔌 Listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"✅ Connection from {addr}")
                conn.settimeout(10)  # 10 seconds timeout
                buffer = b''
                try:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        buffer += data
                except socket.timeout:
                    print("⏰ Timed out waiting for data.")
                if buffer:
                    print("📦 Raw HL7 Data:")
                    print(repr(buffer.decode(errors="ignore")))
                else:
                    print("⚠️ No data received from device.")


if __name__ == "__main__":
    start_server()