#!/usr/bin/env python3
"""
Genesis-OS Neural Link: Phase → Voltage Converter

This script transforms Genesis-OS phase optimization results into
hardware voltage signals for photonic quantum chip control.

Formula: V = (Phase / 2π) * V_pi + V_bias

Hardware Specs (Lithium Niobate Modulators):
- V_pi = 5.2V (half-wave voltage)
- V_bias = 0.0V (DC offset)
- V_max = 8.0V (safety clamp)
- DAC resolution: 16-bit (0-65535)

Author: Genesis-OS Bridge Protocol
Date: 2026-01-29
"""

import json
import csv
import argparse
import os
from pathlib import Path
import math


def load_phases(json_path):
    """Load phase parameters from Genesis Bridge optimization results."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    phases = data['final_solution']['phases']
    n_modes = len(phases)

    # Convert from dict to list (sorted by mode number)
    phase_list = [phases[f'mode_{i}'] for i in range(n_modes)]

    return phase_list, data


def phase_to_voltage(phase_rad, v_pi=5.2, v_bias=0.0):
    """
    Convert phase (radians) to voltage (Volts).

    Formula: V = (Phase / 2π) * V_pi + V_bias

    Args:
        phase_rad: Phase parameter in radians [0, 2π]
        v_pi: Half-wave voltage in Volts
        v_bias: DC bias offset in Volts

    Returns:
        Voltage in Volts
    """
    voltage = (phase_rad / (2 * math.pi)) * v_pi + v_bias
    return voltage


def voltage_to_dac(voltage, v_max=8.0, dac_bits=16):
    """
    Convert voltage to DAC digital value.

    Args:
        voltage: Voltage in Volts [0, V_max]
        v_max: Maximum voltage (corresponds to DAC max value)
        dac_bits: DAC resolution in bits

    Returns:
        DAC integer value [0, 2^bits - 1]
    """
    dac_max = (2 ** dac_bits) - 1

    # Clamp voltage to [0, V_max]
    voltage_clamped = max(0.0, min(voltage, v_max))

    # Linear mapping: V → DAC
    dac_value = int((voltage_clamped / v_max) * dac_max)

    return dac_value


def generate_voltage_map(phase_list, v_pi=5.2, v_bias=0.0, v_max=8.0):
    """
    Generate complete voltage map from phase list.

    Args:
        phase_list: List of phase values in radians
        v_pi: Half-wave voltage
        v_bias: DC bias offset
        v_max: Maximum voltage (safety clamp)

    Returns:
        List of dictionaries with Channel_ID, Phase_Rad, Voltage_V, DAC_Value_16bit
    """
    voltage_map = []

    for channel_id, phase in enumerate(phase_list):
        # Convert phase to voltage
        voltage = phase_to_voltage(phase, v_pi, v_bias)

        # Safety clamp
        voltage_clamped = max(0.0, min(voltage, v_max))

        # Convert to DAC value
        dac_value = voltage_to_dac(voltage_clamped, v_max)

        voltage_map.append({
            'Channel_ID': channel_id,
            'Phase_Rad': phase,
            'Voltage_V': voltage_clamped,
            'DAC_Value_16bit': dac_value
        })

    return voltage_map


def save_voltage_csv(voltage_map, output_path):
    """Save voltage map to CSV file."""
    fieldnames = ['Channel_ID', 'Phase_Rad', 'Voltage_V', 'DAC_Value_16bit']

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(voltage_map)

    print(f"✅ Voltage map saved to: {output_path}")


def print_summary(voltage_map):
    """Print summary statistics of voltage map."""
    voltages = [vm['Voltage_V'] for vm in voltage_map]
    phases = [vm['Phase_Rad'] for vm in voltage_map]

    print("\n" + "="*60)
    print("VOLTAGE MAP SUMMARY")
    print("="*60)
    print(f"Total Channels:       {len(voltage_map)}")
    print(f"\nPhase Statistics (rad):")
    print(f"  Min Phase:           {min(phases):.6f} rad")
    print(f"  Max Phase:           {max(phases):.6f} rad")
    print(f"  Mean Phase:          {sum(phases)/len(phases):.6f} rad")
    print(f"\nVoltage Statistics (V):")
    print(f"  Min Voltage:         {min(voltages):.4f} V")
    print(f"  Max Voltage:         {max(voltages):.4f} V")
    print(f"  Mean Voltage:        {sum(voltages)/len(voltages):.4f} V")
    print(f"\nDAC Statistics (16-bit):")
    print(f"  Min DAC:             {min(vm['DAC_Value_16bit'] for vm in voltage_map)}")
    print(f"  Max DAC:             {max(vm['DAC_Value_16bit'] for vm in voltage_map)}")
    print(f"  Mean DAC:            {sum(vm['DAC_Value_16bit'] for vm in voltage_map) // len(voltage_map)}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Generate voltage map from Genesis-OS phase optimization results'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='results/genesis_128_blind_lock.json',
        help='Input JSON file with phase parameters (default: results/genesis_128_blind_lock.json)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='results/genesis_128_voltage_map.csv',
        help='Output CSV file with voltage map (default: results/genesis_128_voltage_map.csv)'
    )
    parser.add_argument(
        '--v-pi',
        type=float,
        default=5.2,
        help='Half-wave voltage in Volts (default: 5.2V for Lithium Niobate)'
    )
    parser.add_argument(
        '--v-bias',
        type=float,
        default=0.0,
        help='DC bias offset in Volts (default: 0.0V)'
    )
    parser.add_argument(
        '--v-max',
        type=float,
        default=8.0,
        help='Maximum voltage for safety clamp (default: 8.0V)'
    )

    args = parser.parse_args()

    # Load phase data
    print(f"📖 Loading phase data from: {args.input}")
    phase_list, metadata = load_phases(args.input)

    # Generate voltage map
    print(f"⚡ Generating voltage map...")
    print(f"   V_pi = {args.v_pi}V")
    print(f"   V_bias = {args.v_bias}V")
    print(f"   V_max (safety clamp) = {args.v_max}V")

    voltage_map = generate_voltage_map(phase_list, args.v_pi, args.v_bias, args.v_max)

    # Save to CSV
    save_voltage_csv(voltage_map, args.output)

    # Print summary
    print_summary(voltage_map)

    print(f"\n✅ Operation Neural Link complete!")
    print(f"🔌 Ready to connect Genesis-OS to photonic hardware.")
    print(f"📁 Output file: {args.output}")


if __name__ == '__main__':
    main()
