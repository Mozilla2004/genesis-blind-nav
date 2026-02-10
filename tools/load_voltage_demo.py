import csv

def load_voltage_map(filepath):
    """Loads voltage map and simulates hardware writing."""
    print(f"Loading map from {filepath}...")
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Simulate writing 16-bit DAC value to hardware channel
            print(f"Channel {row['Channel_ID']}: Writing DAC={row['DAC_Value_16bit']} (V={row['Voltage_V']})")

if __name__ == "__main__":
    load_voltage_map('results/genesis_128_voltage_map.csv')
