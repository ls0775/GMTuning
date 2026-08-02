#!/usr/bin/env python3
"""
MAF to Virtual VE (VVE) Generator matching exact VVE C6 grid layout.

Grid Specs (matching VVE C6.xlsx / GM E38 VCM Editor Virtual VE Table):
  • MAP Rows (39 steps): 10.0, 12.5, 15.0, ..., 105.0 kPa (step 2.5 kPa)
  • RPM Columns (31 steps): 400, 600, 800, ..., 6400 RPM (step 200 RPM)
"""

import sys
import os
import pandas as pd
import numpy as np

def generate_vve_matching_c6(csv_path, engine_displacement_l=5.967):
    print(f"=== MAF to VVE Generator (Matching VVE C6.xlsx Grid Layout) ===")
    print(f"Input Log: {os.path.basename(csv_path)}")
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

    # Filter for warm, steady-state cruise conditions
    df['dMAP'] = df[map_col].diff().abs() / df[offset_col].diff()
    steady_df = df[(df[ect_col] >= 75.0) & (df['dMAP'] <= 5.0)].copy()

    print(f"Filtered Steady-State Data Frames: {len(steady_df)} / {len(df)}")

    # Exact Grid Breakpoints from VVE C6.xlsx
    rpm_cols = list(range(400, 6600, 200)) # 400, 600, ..., 6400 (31 columns)
    map_rows = [round(x, 1) for x in np.arange(10.0, 107.5, 2.5)] # 10.0, 12.5, ..., 105.0 (39 rows)

    # Compute Ideal Gas Law Theoretical Airflow (g/s)
    # Theoretical Mass Airflow (g/s) = (MAP_Pa * Disp_m3 * RPM / 120) / (R_air * T_k) * 1000 g/kg
    v_disp_m3 = engine_displacement_l / 1000.0
    r_air = 287.058
    
    t_k = steady_df[iat_col] + 273.15
    map_pa = steady_df[map_col] * 1000.0
    rpm = steady_df[rpm_col]
    
    m_dot_theo_gs = (map_pa * v_disp_m3 * (rpm / 120.0)) / (r_air * t_k) * 1000.0
    steady_df['Absolute_VE_%'] = (steady_df[maf_gs_col] / m_dot_theo_gs) * 100.0
    steady_df['MAF_vs_VVE_Ratio'] = steady_df[maf_gs_col] / steady_df[vve_air_col]

    # Bin into exact VVE C6 grid
    rpm_bins = [0] + [(rpm_cols[i] + rpm_cols[i+1])/2 for i in range(len(rpm_cols)-1)] + [10000]
    map_bins = [0] + [(map_rows[i] + map_rows[i+1])/2 for i in range(len(map_rows)-1)] + [200]

    steady_df['RPM_Cell'] = pd.cut(steady_df[rpm_col], bins=rpm_bins, labels=rpm_cols)
    steady_df['MAP_Cell'] = pd.cut(steady_df[map_col], bins=map_bins, labels=map_rows)

    ve_matrix = steady_df.groupby(['MAP_Cell', 'RPM_Cell'], observed=False)['Absolute_VE_%'].mean().unstack()
    ratio_matrix = steady_df.groupby(['MAP_Cell', 'RPM_Cell'], observed=False)['MAF_vs_VVE_Ratio'].mean().unstack()
    count_matrix = steady_df.groupby(['MAP_Cell', 'RPM_Cell'], observed=False)['Absolute_VE_%'].count().unstack()

    # Reindex to force full 39x31 grid matching VVE C6.xlsx exactly
    ve_matrix = ve_matrix.reindex(index=map_rows, columns=rpm_cols)
    ratio_matrix = ratio_matrix.reindex(index=map_rows, columns=rpm_cols)
    count_matrix = count_matrix.reindex(index=map_rows, columns=rpm_cols).fillna(0).astype(int)

    # Save to Excel matching VVE C6.xlsx layout
    base_out = os.path.splitext(csv_path)[0] + "_VVE_C6_Format"
    excel_out = base_out + ".xlsx"
    csv_out = base_out + ".csv"

    with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
        ve_matrix.round(2).to_excel(writer, sheet_name='Absolute VE %')
        ratio_matrix.round(3).to_excel(writer, sheet_name='MAF vs VVE Multiplier')
        count_matrix.to_excel(writer, sheet_name='Sample Count')

    ve_matrix.round(2).to_csv(csv_out)

    print(f"\n✓ Generated VVE Table matching VVE C6.xlsx grid layout:")
    print(f"  • Excel File: {excel_out}")
    print(f"  • CSV File: {csv_out}")
    print(f"  • Grid Shape: {ve_matrix.shape[0]} MAP Rows (10.0 - 105.0 kPa) x {ve_matrix.shape[1]} RPM Columns (400 - 6400 RPM)")

    print("\n--- Preview of Generated VVE Absolute % Table (3200-4000 RPM x 30-80 kPa) ---")
    sub_table = ve_matrix.loc[30.0:80.0, [2400, 2800, 3200, 3600, 4000]]
    print(sub_table.round(1).to_string())

if __name__ == '__main__':
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'HP Tuners/VCM Scanner/Logs/26-07-31 13-43-06.csv'
    generate_vve_matching_c6(csv_file)
