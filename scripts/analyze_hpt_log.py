#!/usr/bin/env python3
"""
VCM Scanner CSV Log Analyzer with Wideband Transport Delay Adjustment.

Usage:
    python scripts/analyze_hpt_log.py <path_to_csv> [--delay_ms DELAY_MS]

Example:
    python scripts/analyze_hpt_log.py "HP Tuners/VCM Scanner/Logs/2026-07-29 MAF Only - MAF Changes 3.csv" --delay_ms -330
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np

def analyze_log(csv_path, delay_ms=0.0):
    delay_sec = delay_ms / 1000.0
    print(f"=== VCM Scanner Log Analysis: {os.path.basename(csv_path)} ===")
    print(f"Wideband Transport Delay Adjustment: {delay_ms:+.1f} ms ({delay_sec:+.3f} s)")
    
    # Locate header row
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("Offset,"):
            header_idx = i
            break
            
    if header_idx is None:
        print("Error: Could not locate 'Offset,' header line in CSV.")
        return

    df = pd.read_csv(csv_path, skiprows=header_idx)
    # Drop unit row (row index 0 after skiprows)
    if 'rpm' in str(df.iloc[0].values).lower() or 's' in str(df.iloc[0].values).lower():
        df = df.iloc[1:].reset_index(drop=True)

    # Clean up column names
    df.columns = [c.strip() for c in df.columns]

    # Convert numeric columns
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Key Channels Identification
    offset_col = 'Offset'
    rpm_col = [c for c in df.columns if 'Engine RPM' in c or 'RPM' in c][0]
    map_col = [c for c in df.columns if 'Manifold Absolute Pressure' in c or 'MAP' in c][0]
    maf_hz_col = [c for c in df.columns if 'Mass Airflow Sensor' in c or 'MAF' in c and 'Hz' in str(c)][0]
    cmd_col = [c for c in df.columns if 'Equivalence Ratio Commanded' in c or 'EQ' in c and 'Cmd' in c][0]
    wb_col = [c for c in df.columns if 'Innovate' in c or 'LC-1' in c or 'Wideband' in c or 'WB' in c or 'Lambda' in c][-1]
    kr_col = [c for c in df.columns if 'Knock Retard' in c][0]
    spark_col = [c for c in df.columns if 'Timing Advance' in c or 'Spark' in c][0]
    ect_col = [c for c in df.columns if 'Coolant Temp' in c or 'ECT' in c][0]
    iat_col = [c for c in df.columns if 'Intake Air Temp' in c or 'IAT' in c][0]

    # Apply Wideband Delay Shift if specified
    # If delay_ms is negative (e.g. -330 ms wideband lag), WB reading at time (t - delay_sec) corresponds to ECU at time t.
    if delay_ms != 0.0:
        # Interpolate Wideband values at (Offset - delay_sec)
        target_times = df[offset_col] - delay_sec
        df['WB_Aligned'] = np.interp(target_times, df[offset_col], df[wb_col])
        wb_analysis_col = 'WB_Aligned'
    else:
        wb_analysis_col = wb_col

    # Calculate EQ Error %
    df['EQ_Error_Pct'] = (df[wb_analysis_col] - df[cmd_col]) / df[cmd_col] * 100.0

    print(f"\n--- Log Overview ---")
    print(f"Duration: {df[offset_col].min():.2f}s to {df[offset_col].max():.2f}s (Total: {df[offset_col].max() - df[offset_col].min():.2f}s, Rows: {len(df)})")
    print(f"RPM Range: {df[rpm_col].min():.0f} - {df[rpm_col].max():.0f} RPM")
    print(f"MAP Range: {df[map_col].min():.1f} - {df[map_col].max():.1f} kPa")
    print(f"MAF Frequency Range: {df[maf_hz_col].min():.1f} - {df[maf_hz_col].max():.1f} Hz")
    print(f"ECT: {df[ect_col].min():.1f}°C to {df[ect_col].max():.1f}°C | IAT: {df[iat_col].min():.1f}°C to {df[iat_col].max():.1f}°C")

    # Knock Analysis
    kr_df = df[df[kr_col] > 0]
    print(f"\n--- Knock Retard (KR) Analysis ---")
    if len(kr_df) == 0:
        print("✓ Zero Knock Retard detected in log.")
    else:
        print(f"⚠️ {len(kr_df)} frames with Knock Retard detected! Max KR: {df[kr_col].max():.2f}°")
        print(kr_df[[offset_col, rpm_col, map_col, maf_hz_col, kr_col, spark_col]].head(10).to_string(index=False))

    # Power Enrichment / WOT Analysis
    pe_df = df[df[cmd_col] < 0.95]
    print(f"\n--- Power Enrichment (PE / WOT) Analysis ---")
    print(f"PE Frames (Cmd EQ < 0.95): {len(pe_df)}")
    if len(pe_df) > 0:
        avg_pe_cmd = pe_df[cmd_col].mean()
        avg_pe_wb = pe_df[wb_analysis_col].mean()
        avg_pe_err = pe_df['EQ_Error_Pct'].mean()
        print(f"Avg Commanded Lambda: {avg_pe_cmd:.3f} | Avg Aligned WB Lambda: {avg_pe_wb:.3f} | Avg EQ Error: {avg_pe_err:+6.2f}%")

    # MAF Frequency Binned Summary
    bins = [2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 12000]
    df['MAF_Bin'] = pd.cut(df[maf_hz_col], bins=bins)
    
    print(f"\n--- MAF Frequency Binned EQ Error % (Delay Adjusted: {delay_ms:+.1f} ms) ---")
    grouped = df.groupby('MAF_Bin', observed=False).agg(
        Count=('EQ_Error_Pct', 'count'),
        Avg_Cmd_Lambda=(cmd_col, 'mean'),
        Avg_Aligned_WB=(wb_analysis_col, 'mean'),
        Avg_Error_Pct=('EQ_Error_Pct', 'mean'),
        Min_Error_Pct=('EQ_Error_Pct', 'min'),
        Max_Error_Pct=('EQ_Error_Pct', 'max')
    ).reset_index()
    
    print(grouped.to_string(index=False))

    # Recommended Tuning Actions
    print(f"\n--- Recommended Tuning Commentary & Actions (After -330ms Delay Shift) ---")
    for _, row in grouped.iterrows():
        if row['Count'] > 5:
            maf_bin = row['MAF_Bin']
            avg_err = row['Avg_Error_Pct']
            if avg_err > 1.5:
                print(f"• MAF Range {maf_bin} Hz is LEAN by {avg_err:+.2f}% -> ADD fuel to MAF table (multiply by {(1 + avg_err/100):.4f})")
            elif avg_err < -1.5:
                print(f"• MAF Range {maf_bin} Hz is RICH by {avg_err:+.2f}% -> REMOVE fuel from MAF table (multiply by {(1 + avg_err/100):.4f})")
            else:
                print(f"• MAF Range {maf_bin} Hz is ON TARGET ({avg_err:+.2f}% error)")

def main():
    parser = argparse.ArgumentParser(description="Analyze VCM Scanner CSV log files with wideband delay correction.")
    parser.add_argument("csv_path", nargs="?", default="HP Tuners/VCM Scanner/Logs/2026-07-29 MAF Only - MAF Changes 3.csv", help="Path to VCM Scanner CSV log file.")
    parser.add_argument("--delay_ms", type=float, default=0.0, help="Wideband transport delay in milliseconds (e.g. -330).")
    
    args = parser.parse_args()
    analyze_log(args.csv_path, args.delay_ms)

if __name__ == '__main__':
    main()
