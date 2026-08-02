#!/usr/bin/env python3
"""
HP Tuners HPL Log Parser & Converter
Extracts log data from HP Tuners .hpl binary log files and converts them to CSV or analyzes them directly.
"""

import sys
import os
import re
import struct
import zlib
import pandas as pd
import numpy as np

def parse_hpl(hpl_path):
    print(f"Reading HPL file: {hpl_path}")
    with open(hpl_path, 'rb') as f:
        data = f.read()

    sync_offsets = [m.start() for m in re.finditer(b'SYNC', data)]
    print(f"Found {len(sync_offsets)} SYNC blocks.")

    # Decompress all CDG data blocks
    decompressed_blocks = []
    for i, sync_off in enumerate(sync_offsets):
        cdg_off = data.find(b'CDG', sync_off)
        if cdg_off != -1 and cdg_off < sync_off + 64:
            comp_len, uncomp_len = struct.unpack('<HH', data[cdg_off+4:cdg_off+8])
            raw_payload = data[cdg_off+12:cdg_off+12+comp_len]
            try:
                decomp = zlib.decompress(raw_payload, -zlib.MAX_WBITS)
                decompressed_blocks.append(decomp)
            except Exception:
                try:
                    decomp = zlib.decompress(raw_payload)
                    decompressed_blocks.append(decomp)
                except Exception:
                    pass

    print(f"Successfully decompressed {len(decompressed_blocks)} blocks.")

    # Extract all text strings from header block (block 0 and start of data)
    header_bytes = data[:sync_offsets[1]] if len(sync_offsets) > 1 else data[:10000]
    
    # Extract channel names and units
    channel_matches = re.findall(rb'[A-Za-z0-9 _\-\%\/\.\(\)\#]{2,}', header_bytes)
    channel_strings = [m.decode('ascii', errors='ignore').strip() for m in channel_matches if len(m.strip()) > 2]
    
    print("\nChannels & Parameters found in HPL header:")
    known_channels = []
    for s in channel_strings:
        if any(k in s.lower() for k in ['rpm', 'maf', 'map', 'spark', 'knock', 'lambda', 'trim', 'fuel', 'speed', 'temp', 'volt', 'tps', 'pedal', 'innovate', 'lc-1', 'eq']):
            if s not in known_channels:
                known_channels.append(s)
                print(f"  • {s}")

    return decompressed_blocks, known_channels

if __name__ == '__main__':
    hpl_file = sys.argv[1] if len(sys.argv) > 1 else './HP Tuners/VCM Scanner/Logs/26-07-31 13-43-06.hpl'
    parse_hpl(hpl_file)
