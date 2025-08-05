import socket
import json
import re

HOST = "0.0.0.0"
PORT = 2575

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

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"[HL7 Server] Listening on {HOST}:{PORT} ...")
        while True:
            conn, addr = srv.accept()
            with conn:
                print(f"\n[Connection from {addr}]")
                data = b''
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                if not data:
                    continue

                try:
                    text = data.decode('utf-8', errors='ignore')
                except Exception:
                    text = data.decode('latin-1', errors='ignore')

                # Strip HL7 framing characters if present (VT \x0b at start, FS \x1c + CR \x0d at end)
                text = text.lstrip('\x0b').rstrip('\x1c\r\n')
                print("[Raw HL7 Message]:")
                # for readability show each segment on its own line
                print(normalize_segments(text).replace('\r', '\n'))

                results = parse_hl7_message(text)
                if results:
                    print("\n[Extracted Lab Results]:")
                    for name, val in results.items():
                        print(f"  {name}: {val}")
                    with open("latest_lab_results.json", "w", encoding="utf-8") as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    print("\nSaved to latest_lab_results.json")
                else:
                    print("⚠️ No OBX results parsed.")


if __name__ == "__main__":
    start_server()