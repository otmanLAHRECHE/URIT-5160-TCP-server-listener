import re
def parse_hl7(hl7_raw):
    results = []
    lines = re.split(r'\r?\n', hl7_raw)

    for line in lines:
        if line.startswith('OBX'):
            fields = line.split('|')
            if len(fields) > 6:
                test_code = fields[3]  # e.g. BASO%^...
                test_value = fields[5].strip() or fields[6].strip()

                if not test_value:
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

    return results