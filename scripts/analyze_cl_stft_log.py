#!/usr/bin/env python3
"""
VCM Scanner Cold Start & Closed-Loop (STFT Enabled) Log Analyzer
Analyzes STFT Bank 1 / Bank 2, ECT Warmup, MAF Hz Trims, VVE MAP/RPM Trims, and Tip-In Response.
"""

import sys
import os
import pandas as pd
import numpy as np

def analyze_cl_stft(csv_path):
    print(f"=== Closed-Loop (STFT Enabled) Cold Start Analysis: {os.path.basename(csv_path)} ===")
    
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    header_idx = [i for i, line in enumerate(lines) if line.startswith("Offset,")][0]
    df = pd.read_csv(csv_path, skiprows=header_idx)
    if 'rpm' in str(df.iloc[0].values).lower() or 's' in str(df.iloc[0].values).lower():
        df = df.iloc[1:].reset_index(drop=True)

    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    offset_col = 'Offset'
    rpm_col = [c for c in df.columns if 'Engine RPM' in c or 'RPM' in c][0]
    map_col = [c for c in df.columns if 'Manifold Absolute Pressure' in c or 'MAP' in c][0]
    maf_hz_col = [c for c in df.columns if 'Mass Airflow Sensor' in c or 'MAF' in c and 'Hz' in str(c)][0]
    maf_gs_col = [c for c in df.columns if 'Mass Airflow (SAE)' in c or 'Mass Airflow' in c and 'g/s' in str(c)][0]
    dyn_air_col = [c for c in df.columns if 'Dynamic Airflow' in c][0]
    vve_air_col = [c for c in df.columns if 'Volumetric Efficiency Airflow' in c][0]
    stft1_col = [c for c in df.columns if 'Short Term Fuel Trim Bank 1' in c][0]
    stft2_col = [c for c in df.columns if 'Short Term Fuel Trim Bank 2' in c][0]
    ltft1_col = [c for c in df.columns if 'Long Term Fuel Trim Bank 1' in c][0]
    ltft2_col = [c for c in df.columns if 'Long Term Fuel Trim Bank 2' in c][0]
    kr_col = [c for c in df.columns if 'Knock Retard' in c][0]
    ect_col = [c for c in df.columns if 'Coolant Temp' in c or 'ECT' in c][0]
    iat_col = [c for c in df.columns if 'Intake Air Temp' in c or 'IAT' in c][0]
    cmd_col = [c for c in df.columns if 'Equivalence Ratio Commanded' in c][0]
    wb_col = [c for c in df.columns if 'Innovate' in c or 'LC-1' in c or 'Wideband' in c][-1]
    tps_col = [c for c in df.columns if 'Throttle Position' in c or 'TPS' in c][0]

    # Combine STFT Bank 1 and Bank 2
    df['STFT_Avg_%'] = (df[stft1_col] + df[stft2_col]) / 2.0

    print(f"\n--- Log Overview ---")
    print(f"Total Log Duration: {df[offset_col].min():.1f}s to {df[offset_col].max():.1f}s (Total: {df[offset_col].max() - df[offset_col].min():.1f}s, Rows: {len(df)})")
    print(f"RPM Range: {df[rpm_col].min():.0f} - {df[rpm_col].max():.0f} RPM")
    print(f"MAP Range: {df[map_col].min():.1f} - {df[map_col].max():.1f} kPa")
    print(f"MAF Hz Range: {df[maf_hz_col].min():.1f} - {df[maf_hz_col].max():.1f} Hz")
    print(f"ECT Warmup: {df[ect_col].min():.1f}°C to {df[ect_col].max():.1f}°C | IAT: {df[iat_col].min():.1f}°C to {df[iat_col].max():.1f}°C")

    # Closed-Loop Status & Readiness
    max_ltft = max(df[ltft1_col].abs().max(), df[ltft2_col].abs().max())
    print(f"\n--- Fuel Trim System Status ---")
    if max_ltft == 0:
        print("✓ LTFTs are DISABLED (0.0%), STFTs active — perfect per E38 reflash rules.")
    else:
        print(f"⚠️ LTFTs are ACTIVE (Max LTFT: {max_ltft:.1f}%).")

    # Warm Engine Filter (ECT >= 75°C, Stoich Commanded)
    warm_cl_df = df[(df[ect_col] >= 75.0) & (df[cmd_col] >= 0.98) & (df[cmd_col] <= 1.02)].copy()
    print(f"\n--- Warm Closed-Loop Steady-State Analysis (ECT >= 75°C) ---")
    print(f"Warm CL Frames: {len(warm_cl_df)} / {len(df)}")
    
    if len(warm_cl_df) > 0:
        stft1_mean = warm_cl_df[stft1_col].mean()
        stft2_mean = warm_cl_df[stft2_col].mean()
        stft_comb = warm_cl_df['STFT_Avg_%'].mean()
        print(f"STFT Bank 1 Avg: {stft1_mean:+5.2f}% | STFT Bank 2 Avg: {stft2_mean:+5.2f}% | Combined STFT: {stft_comb:+5.2f}%")
        print(f"Bank 1 vs Bank 2 Imbalance: {(stft1_mean - stft2_mean):+5.2f}%")

        # MAF Frequency Binned STFT Summary
        bins = [2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 8000]
        warm_cl_df['MAF_Bin'] = pd.cut(warm_cl_df[maf_hz_col], bins=bins)

        print(f"\n--- MAF Frequency STFT Trim Summary ---")
        maf_summary = warm_cl_df.groupby('MAF_Bin', observed=False).agg(
            Count=('STFT_Avg_%', 'count'),
            STFT1_Avg=(stft1_col, 'mean'),
            STFT2_Avg=(stft2_col, 'mean'),
            Combined_STFT=('STFT_Avg_%', 'mean'),
            Min_STFT=('STFT_Avg_%', 'min'),
            Max_STFT=('STFT_Avg_%', 'max')
        ).reset_index()
        print(maf_summary.to_string(index=False))

    # Knock Analysis
    kr_df = df[df[kr_col] > 0]
    print(f"\n--- Knock Retard (KR) Analysis ---")
    if len(kr_df) == 0:
        print("✓ Zero Knock Retard detected across entire log!")
    else:
        print(f"⚠️ {len(kr_df)} frames with Knock Retard detected. Max KR: {df[kr_col].max():.2f}°")
        print(kr_df[[offset_col, rpm_col, map_col, maf_hz_col, kr_col]].head(10).to_string(index=False))

    # Tip-In Dynamic Airflow vs MAF Inspection
    # Find fast pedal / TPS deltas
    df['dTPS'] = df[tps_col].diff() / df[offset_col].diff()
    tip_ins = df[(df['dTPS'] > 50.0) & (df[rpm_col] > 1000)].copy()
    print(f"\n--- Dynamic Airflow vs MAF Tip-In Inspection ---")
    print(f"Rapid Throttle Tip-In Events Detected: {len(tip_ins)}")
    if len(tip_ins) > 0:
        tip_ins['MAF_vs_Dyn_Err_%'] = (tip_ins[maf_gs_col] - tip_ins[dyn_air_col]) / tip_ins[dyn_air_col] * 100.0
        print(tip_ins[[offset_col, rpm_col, map_col, maf_hz_col, maf_gs_col, dyn_air_col, vve_air_col, 'MAF_vs_Dyn_Err_%']].head(10).to_string(index=False))

if __name__ == '__main__':
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'HP Tuners/VCM Scanner/Logs/26-08-02 12-21-01.csv'
    analyze_cl_stft(csv_file)
