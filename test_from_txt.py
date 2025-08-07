# File: test_from_txt.py
from parse_hl7 import parse_hl7
import json
import re

# Read the raw HL7 message
with open("received_hl7.txt", "r", encoding="utf-8") as file:
    raw_hl7 = file.read()

# Normalize line endings (just in case)
lines = re.split(r'\r?\n', raw_hl7)

# Try to extract the test/exam ID from OBR segment (field 3)
exam_id = None
for line in lines:
    if line.startswith("OBR") and len(line.split('|')) > 3:
        exam_id = line.split('|')[3].strip()
        break

# Parse the OBX results
obx_results = parse_hl7(raw_hl7)

if obx_results:
    result_json = {
        item["name"]: item["value"]
    for item in obx_results
    if item["value"] and len(item["value"]) < 100
    }

    # Determine the JSON filename
    if exam_id:
        filename = f"malade_n_{exam_id}.json"
    else:
        filename = "malade_n_unknown.json"

    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(result_json, json_file, indent=2)

    print(f"\n✅ HL7 results exported to: {filename}")
else:
    print("⚠️ No OBX results found in the HL7 data.")
