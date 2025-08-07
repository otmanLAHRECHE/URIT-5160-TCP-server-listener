import socket
import datetime
import threading
import time
import uuid
import json
import re
from parse_hl7 import parse_hl7

HOST = "0.0.0.0"
PORT = 5000
running = True
receiving_data = False

def progress_thread():
    while running:
        if receiving_data:
            print("📡 Receiving HL7 data...", end='\r')
        else:
            print("⏳ Waiting for incoming connection...", end='\r')
        time.sleep(2)

threading.Thread(target=progress_thread, daemon=True).start()

print(f"🖥️ HL7 Server listening on {HOST}:{PORT}")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

while True:
    receiving_data = False
    client_socket, client_address = server_socket.accept()
    print(f"\n✅ Connection from {client_address}")
    receiving_data = True

    buffer = b""
    client_socket.settimeout(15)
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            buffer += data
    except socket.timeout:
        print("\n⚠️ Timed out waiting for data from client.")

    decoded = buffer.decode(errors="ignore")
    print("\n📦 Raw HL7 Data (truncated):")
    print(decoded[:500], "..." if len(decoded) > 500 else "")

    # Save only latest message
    with open("received_hl7.txt", "w", encoding="utf-8") as f:
        f.write(decoded)

    # Parse OBX results
    obx_results = parse_hl7(decoded)
    if obx_results:
        # Filter out empty or too-long values
        result_json = {
            item["name"]: item["value"]
            for item in obx_results
            if item["value"] and len(item["value"]) < 100
        }

        if result_json:
            # Extract exam ID from OBR segment
            exam_id = None
            lines = re.split(r'\r?\n', decoded)
            for line in lines:
                if line.startswith("OBR") and len(line.split('|')) > 3:
                    exam_id = line.split('|')[3].strip()
                    break

            if exam_id:
                filename = f"malade_n_{exam_id}.json"
            else:
                filename = f"hl7_result_{uuid.uuid4()}.json"

            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(result_json, json_file, indent=2)

            print(f"\n✅ OBX results saved to {filename}")
        else:
            print("⚠️ No valid OBX values after filtering.")
    else:
        print("⚠️ No OBX results parsed.")

    client_socket.close()
    receiving_data = False