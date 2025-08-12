import re
def parse_hl7(hl7_raw):
    results = []
    lines = re.split(r'\r?\n', hl7_raw)

    print("\n🔍 Scanning for OBX lines...")
    for line in lines:
        if line.startswith('OBX'):
            print(f"➡️  Found OBX: {line}")
            fields = line.split('|')

            # Ensure we have at least 7 fields
            if len(fields) < 7:
                print(f"⚠️ Skipping OBX (too few fields): {fields}")
                continue

            test_code = fields[3]
            test_value = fields[5].strip() or fields[6].strip()
            
            # Skip if value is empty
            if not test_value:
                print(f"⚠️ Skipping OBX (empty value): {fields}")
                continue

            if '^' in test_code:
                parts = test_code.split('^')
                test_name = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            else:
                test_name = test_code.strip()

            results.append({
                "name": test_name,
                "value": test_value
            })

    print(f"✅ Total OBX results parsed: {len(results)}")
    return results
