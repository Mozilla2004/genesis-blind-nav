import csv
import sys

def verify_csv(filepath, v_max=8.0):
    print(f"Verifying {filepath} against V_max={v_max}...")
    violations = []
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    voltage = float(row['Voltage_V'])
                    if voltage > v_max:
                        violations.append(row)
                except ValueError:
                    print(f"Error parsing row: {row}")

        if violations:
            print(f"❌ Found {len(violations)} violations!")
            for v in violations:
                print(f"  Channel {v['Channel_ID']}: {v['Voltage_V']} V")
            sys.exit(1)
        else:
            print("✅ No violations found. All voltages <= 8.0V.")
            sys.exit(0)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)

if __name__ == "__main__":
    verify_csv('results/genesis_128_voltage_map.csv')
