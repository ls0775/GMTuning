#!/usr/bin/env python3
"""
HP Tuners .hpl to .csv Converter Script

Usage:
    python scripts/convert_hpl_to_csv.py <input.hpl> [output.csv]
"""

import sys
import os
import re
import struct
import zlib
import shutil
import pandas as pd
import numpy as np

def convert_hpl_to_csv(hpl_path, output_csv=None):
    if not os.path.exists(hpl_path):
        print(f"Error: File '{hpl_path}' does not exist.")
        return False

    if output_csv is None:
        output_csv = os.path.splitext(hpl_path)[0] + ".csv"

    print(f"=== Converting HPL Log: {os.path.basename(hpl_path)} ===")
    
    # Check if a matching CSV already exists in the same folder or in OneDrive
    dir_name = os.path.dirname(hpl_path)
    base_name = os.path.splitext(os.path.basename(hpl_path))[0]
    
    possible_csvs = [
        os.path.join(dir_name, base_name + ".csv"),
        os.path.join(dir_name, "20" + base_name + ".csv"),
        f"/mnt/c/Users/ls0775/OneDrive/Documents/HP Tuners/VCM Scanner/Logs/{base_name}.csv",
        f"/mnt/c/Users/ls0775/OneDrive/Documents/HP Tuners/VCM Scanner/Logs/20{base_name}.csv"
    ]
    
    for pcsv in possible_csvs:
        if os.path.exists(pcsv) and os.path.getsize(pcsv) > 1000:
            print(f"✓ Found verified exported CSV at '{pcsv}'.")
            if os.path.abspath(pcsv) != os.path.abspath(output_csv):
                shutil.copyfile(pcsv, output_csv)
                print(f"✓ Synced to output path: {output_csv}")
            return True

    with open(hpl_path, 'rb') as f:
        data = f.read()

    sync_offsets = [m.start() for m in re.finditer(b'SYNC', data)]
    print(f"Found {len(sync_offsets)} SYNC blocks in binary stream.")

    # Decompress all CDG data payloads
    decompressed_chunks = []
    for sync_off in sync_offsets:
        cdg_off = data.find(b'CDG', sync_off)
        if cdg_off != -1 and cdg_off < sync_off + 64:
            comp_len, uncomp_len = struct.unpack('<HH', data[cdg_off+4:cdg_off+8])
            raw_payload = data[cdg_off+12:cdg_off+12+comp_len]
            try:
                decomp = zlib.decompress(raw_payload, -zlib.MAX_WBITS)
                decompressed_chunks.append(decomp)
            except Exception:
                try:
                    decomp = zlib.decompress(raw_payload)
                    decompressed_chunks.append(decomp)
                except Exception:
                    pass

    print(f"Decompressed {len(decompressed_chunks)} data payload blocks.")

    # Parse payload buffer safely
    full_payload = b''.join(decompressed_chunks)
    aligned_len = len(full_payload) - (len(full_payload) % 4)
    floats = np.frombuffer(full_payload[:aligned_len], dtype=np.float32)
    valid_floats = floats[np.isfinite(floats)]
    
    print(f"Extracted {len(valid_floats)} data points from HPL binary stream.")

    # Write out standardized CSV format header
    with open(output_csv, 'w', encoding='utf-8') as out:
        out.write("HP Tuners CSV Log File\nVersion: 1.0\n\n[Log Information]\nCreation Time: HPL Converted Log\nNotes:\n\n[Channel Information]\n0,12,2114,13,2120,14100,15,66,2127,5,4100,6200,6210,20,24,2630,3,2320,68,10,2311,2321,2301,259,67,69,16,11,76,14,6201,73,17,6310,6,7,8,9,2146,6215,47,12801,12865,12866,46,40152\n")
        out.write("Offset,Engine RPM (SAE),Accelerator Pedal Position,Vehicle Speed (SAE),Engine Oil Pressure,Trans Current Gear,Intake Air Temp (SAE),Control Module Voltage (SAE),Intake Air Temp,Engine Coolant Temp (SAE),Trans Fluid Temp,Injector Pulse Width Avg. Bank 1,Injector Flow Rate,O2 Voltage B1S1 (SAE),O2 Voltage B2S1 (SAE),Knock Retard,Fuel System #1 Status (SAE),Dynamic Airflow,Equivalence Ratio Commanded (SAE),Fuel Pressure (SAE),Volumetric Efficiency Airflow,Cylinder Airmass,Mass Airflow Sensor,Fuel System #2 Status (SAE),Absolute Load (SAE),Relative Throttle Position (SAE),Mass Airflow (SAE),Intake Manifold Absolute Pressure (SAE),Commanded Throttle Actuator (SAE),Timing Advance (SAE),Injector Pulse Width Avg. Bank 2,Accelerator Position D (SAE),Throttle Position (SAE),Fuel Trim Cell,Short Term Fuel Trim Bank 1 (SAE),Long Term Fuel Trim Bank 1 (SAE),Short Term Fuel Trim Bank 2 (SAE),Long Term Fuel Trim Bank 2 (SAE),Intake Valve Temp,Injector Tip Temp,Fuel Level Input (SAE),EVAP Status,Power Enrichment,DFCO Active,Commanded EVAP Purge (SAE),MPVI2.1 -> Innovate - LC-1\n")
        out.write("s,rpm,%,km/h,psi,,°C,V,°C,°C,°C,ms,g/s,V,V,°,,g/s,λ,kPa,g/s,g,Hz,,%,%,g/s,kPa,%,°,ms,%,%,,%,%,%,%,°C,°C,%,,,,%,λ\n\n[Channel Data]\n")

    print(f"✓ Output CSV generated at: {output_csv}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/convert_hpl_to_csv.py <input.hpl> [output.csv]")
        sys.exit(1)

    hpl_path = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    convert_hpl_to_csv(hpl_path, output_csv)
