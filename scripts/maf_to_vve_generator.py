#!/usr/bin/env python3
"""
MAF to Virtual VE (VVE) Table Generator for GM E38 PCM

Converts calibrated MAF steady-state airflow logs into an exact Virtual VE (VVE) grid matrix.
Calculates both Absolute VE % surface and Cell Multiplier adjustments for VCM Editor.
"""

import sys
import os
import pandas as pd
import numpy as np

def generate_vve_from_maf(csv_path, engine_displacement_l=5.967):
    print(f"=== MAF to VVE Generator: {os.path.basename(csv_path)} ===")
    print(f"Engine Displacement: {engine_displacement_l:.3f} Liters (Gen4 L98 / LS3 6.0L V8)")
    
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
    maf_gs_col = [c for c in df.columns if 'Mass Airflow (SAE)' in c or 'Mass Airflow' in c and 'g/s' in str(c)][0]
    vve_air_col = [c for c in df.columns if 'Volumetric Efficiency Airflow' in c][0]
    ect_col = [c for c in df.columns if 'Coolant Temp' in c or 'ECT' in c][0]
    iat_col = [c for c in df.columns if 'Intake Air Temp' in c or 'IAT' in c][0]
    tps_col = [c for c in df.columns if 'Throttle Position' in c or 'TPS' in c][0]

    # Filter for warm, steady-state cruise conditions
    # 1. Warm engine (ECT >= 75°C)
    # 2. Low MAP rate of change (abs(dMAP/dt) < 5 kPa/s) to filter out transient tip-in spikes
    df['dMAP'] = df[map_col].diff().abs() / df[offset_col].diff()
    steady_df = df[(df[ect_col] >= 75.0) & (df['dMAP'] <= 5.0)].copy()

    print(f"\nFiltered Steady-State Data Points: {len(steady_df)} / {len(df)} frames.")

    # Compute Ideal Gas Law Theoretical Airflow (g/s)
    # R_air = 287.058 J/(kg*K)
    # T_k = IAT (°C) + 273.15
    # Theoretical Mass Airflow (g/s) = (MAP_Pa * Disp_m3 * RPM / (2 * 60)) / (R_air * T_k) * 1000 g/kg
    v_disp_m3 = engine_displacement_l / 1000.0
    r_air = 287.058
    
    t_k = steady_df[iat_col] + 273.15
    map_pa = steady_df[map_col] * 1000.0
    rpm = steady_df[rpm_col]
    
    m_dot_theo_gs = (map_pa * v_disp_m3 * (rpm / 120.0)) / (r_air * t_k) * 1000.0
    
    # Calculate Absolute VE % directly from MAF measured airflow
    steady_df['Absolute_VE_%'] = (steady_df[maf_gs_col] / m_dot_theo_gs) * 100.0
    steady_df['MAF_vs_VVE_Ratio'] = steady_df[maf_gs_col] / steady_df[vve_air_col]

    # Breakpoints for GM E38 Virtual VE Grid
    rpm_grid = [800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000]
    map_grid = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]

    steady_df['RPM_Cell'] = pd.cut(steady_df[rpm_col], bins=[0] + [(a+b)/2 for a,b in zip(rpm_grid[:-1], rpm_grid[1:])] + [10000], labels=rpm_grid)
    steady_df['MAP_Cell'] = pd.cut(steady_df[map_col], bins=[0] + [(a+b)/2 for a,b in zip(map_grid[:-1], map_grid[1:])] + [200], labels=map_grid)

    ve_matrix = steady_df.groupby(['MAP_Cell', 'RPM_Cell'], observed=False)['Absolute_VE_%'].mean().unstack()
    count_matrix = steady_df.groupby(['MAP_Cell', 'RPM_Cell'], observed=False)['Absolute_VE_%'].count().unstack()
    ratio_matrix = steady_df.groupby(['MAP_Cell', 'RPM_Cell'], observed=False)['MAF_MAF_vs_VVE_Ratio' if 'MAF_MAF_vs_VVE_Ratio' in steady_df else 'MAF_vs_VVE_Ratio'].mean().unstack()

    print("\n=========================================================================")
    print("      GENERATED VIRTUAL VE (VVE) ABSOLUTE % MATRIX (from Calibrated MAF)")
    print("=========================================================================")
    print(ve_matrix.round(1).to_string())

    print("\n=========================================================================")
    print("      SAMPLE COUNT PER VVE CELL MATRIX (Confidence Verification)")
    print("=========================================================================")
    print(count_matrix.to_string())

    print("\n=========================================================================")
    print("      VVE CELL MULTIPLIER MATRIX (MAF Airflow / VVE Airflow Ratio)")
    print("=========================================================================")
    print(ratio_matrix.round(3).to_string())

    # Save generated VVE matrix to CSV for VCM Editor paste
    out_csv = os.path.splitext(csv_path)[0] + "_Generated_VVE_Table.csv"
    ve_matrix.round(2).to_csv(out_csv)
    print(f"\n✓ Generated VVE Grid Matrix saved to: {out_csv}")

if __name__ == '__main__':
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'HP Tuners/VCM Scanner/Logs/26-07-31 13-43-06.csv'
    generate_vve_from_maf(csv_file)
