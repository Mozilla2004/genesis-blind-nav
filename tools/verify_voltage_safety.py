#!/usr/bin/env python3
"""
Genesis-OS Safety Verification Tool

This script performs quality assurance (QA) checks on voltage map files
before they are loaded into hardware. It validates:

1. Voltage safety (all voltages <= V_max)
2. DAC value integrity (within 16-bit range)
3. Channel count verification
4. Data format validation
5. Statistical summary

This is the "Safety Net" that protects hardware from incorrect data.

Author: Genesis-OS Bridge Protocol (Jules + CC)
Date: 2026-01-29
Purpose: Quality Assurance before hardware deployment
"""

import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


def verify_csv(
    filepath: str,
    v_max: float = 8.0,
    dac_max: int = 65535,
    expected_channels: int = 128
) -> Tuple[bool, List[str], List[Dict]]:
    """
    Comprehensive CSV verification for Genesis-OS voltage maps.

    Args:
        filepath: Path to CSV file
        v_max: Maximum safe voltage (default: 8.0V)
        dac_max: Maximum DAC value (default: 65535 for 16-bit)
        expected_channels: Expected number of channels (default: 128)

    Returns:
        (is_valid, warnings, violations)
        - is_valid: True if no critical violations
        - warnings: List of warning messages
        - violations: List of violating rows
    """
    print(f"🔍 Genesis-OS Safety Verification")
    print(f"📁 File: {filepath}")
    print(f"⚙️  Parameters: V_max={v_max}V, DAC_max={dac_max}, Channels={expected_channels}")
    print("="*70)

    violations = []
    warnings = []
    channel_count = 0
    voltages = []
    dac_values = []

    # Check if file exists
    if not Path(filepath).exists():
        print(f"❌ ERROR: File not found: {filepath}")
        return False, [f"File not found: {filepath}"], []

    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)

            # Validate CSV headers
            expected_headers = ['Channel_ID', 'Phase_Rad', 'Voltage_V', 'DAC_Value_16bit']
            actual_headers = reader.fieldnames

            if actual_headers != expected_headers:
                warnings.append(
                    f"Header mismatch. Expected: {expected_headers}, "
                    f"Got: {actual_headers}"
                )

            # Verify each row
            for row in reader:
                channel_count += 1

                try:
                    # Extract values
                    channel_id = int(row['Channel_ID'])
                    phase = float(row['Phase_Rad'])
                    voltage = float(row['Voltage_V'])
                    dac_value = int(row['DAC_Value_16bit'])

                    # Store for statistics
                    voltages.append(voltage)
                    dac_values.append(dac_value)

                    # Check 1: Voltage safety (CRITICAL)
                    if voltage > v_max:
                        violations.append({
                            'type': 'CRITICAL',
                            'channel': channel_id,
                            'reason': f'Voltage {voltage:.4f}V exceeds V_max={v_max}V',
                            'row': row
                        })

                    # Check 2: Voltage negative (WARNING)
                    if voltage < 0:
                        warnings.append(
                            f"Channel {channel_id}: Negative voltage {voltage:.4f}V"
                        )

                    # Check 3: DAC value range (CRITICAL)
                    if dac_value < 0 or dac_value > dac_max:
                        violations.append({
                            'type': 'CRITICAL',
                            'channel': channel_id,
                            'reason': f'DAC value {dac_value} out of range [0, {dac_max}]',
                            'row': row
                        })

                    # Check 4: Phase range (WARNING)
                    if phase < 0 or phase > 6.28318530718:
                        warnings.append(
                            f"Channel {channel_id}: Phase {phase:.6f} rad outside [0, 2π]"
                        )

                    # Check 5: Channel ID sequence (WARNING)
                    if channel_id != channel_count - 1:
                        warnings.append(
                            f"Channel ID sequence error: expected {channel_count - 1}, "
                            f"got {channel_id}"
                        )

                except (ValueError, KeyError) as e:
                    violations.append({
                        'type': 'CRITICAL',
                        'channel': channel_id,
                        'reason': f'Parse error: {str(e)}',
                        'row': row
                    })

        # Check 6: Channel count verification
        if channel_count != expected_channels:
            warnings.append(
                f"Channel count mismatch: expected {expected_channels}, "
                f"found {channel_count}"
            )

        # Generate summary statistics
        if voltages:
            v_min = min(voltages)
            v_max_actual = max(voltages)
            v_mean = sum(voltages) / len(voltages)

            print(f"\n📊 STATISTICS")
            print(f"   Channels: {channel_count}")
            print(f"   Voltage range: {v_min:.4f}V → {v_max_actual:.4f}V")
            print(f"   Mean voltage: {v_mean:.4f}V")
            print(f"   DAC range: {min(dac_values)} → {max(dac_values)}")

            if v_max_actual < v_max:
                safety_margin = v_max - v_max_actual
                print(f"   ✅ Safety margin: {safety_margin:.2f}V")

        # Print warnings
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)})")
            for i, warning in enumerate(warnings[:10], 1):  # Show first 10
                print(f"   {i}. {warning}")
            if len(warnings) > 10:
                print(f"   ... and {len(warnings) - 10} more warnings")

        # Print violations
        if violations:
            print(f"\n❌ VIOLATIONS ({len(violations)})")
            for i, v in enumerate(violations[:10], 1):  # Show first 10
                print(f"   {i}. [{v['type']}] Channel {v['channel']}: {v['reason']}")
            if len(violations) > 10:
                print(f"   ... and {len(violations) - 10} more violations")

        # Final verdict
        print("\n" + "="*70)

        if violations:
            print("❌ VERIFICATION FAILED - CRITICAL ISSUES FOUND")
            print("\n🚨 DO NOT LOAD THIS FILE INTO HARDWARE")
            print("   Please review violations and correct the source data.")
            return False, warnings, violations
        else:
            print("✅ VERIFICATION PASSED - FILE IS SAFE FOR HARDWARE")
            print(f"\n✨ All {channel_count} channels verified")
            print(f"✨ All voltages <= {v_max}V")
            print(f"✨ All DAC values in range [0, {dac_max}]")
            if not warnings:
                print("✨ No warnings - perfect quality")
            else:
                print(f"⚠️  {len(warnings)} warnings (non-critical)")
            print("\n✅ This file is approved for hardware deployment.")
            return True, warnings, []

    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {filepath}")
        return False, [f"File not found: {filepath}"], []
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {str(e)}")
        return False, [f"Unexpected error: {str(e)}"], []


def main():
    parser = argparse.ArgumentParser(
        description='Verify Genesis-OS voltage map files for hardware safety'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='results/genesis_128_voltage_map.csv',
        help='Input CSV file to verify (default: results/genesis_128_voltage_map.csv)'
    )
    parser.add_argument(
        '--v-max',
        type=float,
        default=8.0,
        help='Maximum safe voltage in Volts (default: 8.0V)'
    )
    parser.add_argument(
        '--dac-max',
        type=int,
        default=65535,
        help='Maximum DAC value (default: 65535 for 16-bit)'
    )
    parser.add_argument(
        '--channels',
        type=int,
        default=128,
        help='Expected number of channels (default: 128)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with error even on warnings (not just violations)'
    )

    args = parser.parse_args()

    # Run verification
    is_valid, warnings, violations = verify_csv(
        args.input,
        v_max=args.v_max,
        dac_max=args.dac_max,
        expected_channels=args.channels
    )

    # Exit code
    if violations:
        sys.exit(1)  # Critical failures
    elif warnings and args.strict:
        sys.exit(1)  # Warnings treated as errors in strict mode
    else:
        sys.exit(0)  # Success


if __name__ == "__main__":
    main()
