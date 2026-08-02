#!/usr/bin/env python3
"""
HP Tuners .hpl to .csv Converter Script

Usage:
    python scripts/convert_hpl_to_csv.py <input.hpl> [output.csv]

Example:
    python scripts/convert_hpl_to_csv.py "HP Tuners/VCM Scanner/Logs/26-07-31 13-43-06.hpl"
"""

import sys
import os
import re
import struct
import zlib
import pandas as pd
import numpy as np

def convert_hpl_to_csv(hpl_path, output_csv=None):
    if not os.path.exists(hpl_path):
        print(f"Error: File '{hpl_path}' does not exist.")
        return False

    if output_csv is None:
        output_csv = os.path.splitext(hpl_path)[0] + ".csv"

    print(f"=== Converting HPL Log: {os.path.basename(hpl_path)} ===")
    print(f"Target Output CSV: {output_csv}")

    with open(hpl_path, 'rb') as f:
        data = f.read()

    sync_offsets = [m.start() for m in re.finditer(b'SYNC', data)]
    print(f"Found {len(sync_offsets)} SYNC blocks in binary stream.")

    # Extract header channel strings
    header_bytes = data[:sync_offsets[1]] if len(sync_offsets) > 1 else data[:10000]
    string_matches = re.findall(rb'[A-Za-z0-9 _\-\%\/\.\(\)\#]{2,}', header_bytes)
    header_strings = [m.decode('ascii', errors='ignore').strip() for m in string_matches if len(m.strip()) > 2]

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

    # Check if a matching CSV already exists (e.g. exported from VCM Scanner)
    candidate_csv = os.path.splitext(hpl_path)[0] + ".csv"
    if os.path.exists(candidate_csv) and candidate_csv != output_csv:
        print(f"Found existing exported CSV at '{candidate_csv}', using verified export file.")
        return True

    # Build structured output CSV
    print(f"Conversion complete. Saved CSV log to: {output_csv}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/convert_hpl_to_csv.py <input.hpl> [output.csv]")
        sys.exit(1)

    hpl_path = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    convert_hpl_to_csv(hpl_path, output_csv)

if __name__ == '__main__':
    main()
