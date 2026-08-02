# E38 L98 Tuning Workflow Standard Operating Procedure (SOP)

## Scope
Repeatable process for safe reflash tuning of GM Gen IV LS engines (E38 ECM / 6L80E) with HP Tuners.
Primary Method: **Blended MAF Rescale + Virtual VE (VVE) Calibration**.

---

## 1. Course Framework & Transcript Alignment

All session logs, commits, and tune entries must align with the 6-step framework:
1. **Step 1:** Download stock ROM & establish immutable baseline (`Step 1 - Downloading Stock ROM.txt`)
2. **Step 2:** Modification capture & hardware freeze (`Step 2 - What Modifications Have Been Performed.txt`)
3. **Step 3:** Configure base tune file setup (`Step 3 - Configure Base Tune File.txt`)
4. **Step 4:** Air and Fuel scaling — MAF calibration pass -> VVE calibration pass -> Blended restore (`Step 4 - Air and Fuel Scaling.txt`)
5. **Step 5:** Optimise WOT fueling targets & High Octane spark advance (`Step 5 - Optimising the Tune.txt`)
6. **Step 6:** Confirm calibration on road & track (`Step 6 - Confirm Calibration on the Road.txt`)

> [!NOTE]
> All raw course transcripts are preserved in [docs/transcripts/](file:///home/ls0775/source/repos/GMTuning/docs/transcripts/). Refer to [e38-l98-maf-vve-reflash-playbook.md](file:///home/ls0775/source/repos/GMTuning/docs/e38-l98-maf-vve-reflash-playbook.md) for table paths and step-by-step instructions.

---

## 2. Airflow Strategy Decision Tree

1. **Factory MAF present and reliable (preferred for street/track)?**
   - **YES** -> Use **MAF + VVE (Standard E38 Blended Operating Model)**.
   - **NO** -> Proceed to Question 2.
2. **MAF removed/unreliable but staying on factory E38 VVE architecture?**
   - **YES** -> Use **VVE-based Speed Density (MAP) Tuning**.
   - **NO** -> Proceed to Question 3.
3. **Need full traditional VE table workflow via custom OS?**
   - **YES** -> Convert to **1 Bar Speed Density OS**.
   - **NO** -> Reassess hardware/sensor faults before proceeding.

**Current Vehicle Default:** **MAF + VVE (Standard E38)**.

---

## 3. Mandatory Step 2 Baseline Gate

Do not alter calibration until the following baseline metadata is recorded in [docs/vehicle-baseline.md](file:///home/ls0775/source/repos/GMTuning/docs/vehicle-baseline.md):
- Vehicle/Engine/PCM/Trans/Diff parameters
- Intake/MAF duct geometry & injector part numbers
- Header primary diameter, exhaust size, cat configuration
- Camshaft duration, lift, LSA, and valvetrain hardware
- Fuel octane (e.g. 98 RON / E85) and baseline DTC status

---

## 4. Calibration Parameters Summary Matrix

| Step | Subsystem | Action | Parameter / Table Path | Target Value |
|---|---|---|---|---|
| **Step 3** | Torque | Max limits | `Engine -> Torque Mgmt` | Max gear torque, Trans Input Max = **8192 Nm** |
| **Step 3** | Knock Control | Reduce max retard | `Spark -> Retard -> Max Retard` | Multiply table by **0.75** (reduce by 25%) |
| **Step 3** | Knock Control | Disable burst knock | `Spark -> Retard -> Base vs Cyl Air Delta` | Set all cells to **0** |
| **Step 3** | Knock Control | Double decay speed | `Spark -> Retard -> Knock Retard Decay` | Multiply table by **2.0** |
| **Step 3** | Fueling (PE) | PE Throttle entry | `Fuel -> Power Enrichment -> PE Throttle Pedal` | **40%** @ <=2500 RPM, **5%** @ >=4500 RPM |
| **Step 3** | Fueling (PE) | Temporary EQ Target | `Fuel -> Power Enrichment -> EQ Ratio Gas` | **1.174** flat ($\approx 0.85\lambda$ / 12.5 AFR) |
| **Step 3** | Fueling (PE) | Ramp rate & delay | `PE Ramp In Rate` / `PE Delay` | Ramp = **1.0**, Delay = **0 RPM** |
| **Step 3** | Fueling (Trims) | Disable LTFTs | `Fuel -> Open & Closed Loop -> LTFT Enable` | Min ECT = **256°C**, Max ECT = **-40°C** |
| **Step 4A** | MAF Mode | Force MAF operation | `Airflow -> Dynamic -> High RPM Disable/Re-enable` | **400 RPM** / **300 RPM** |
| **Step 4A** | MAF Mode | Disable STFTs | `Closed Loop Enable ECT` / `O2 Readiness ECT` | Set both to **256°C** |
| **Step 4A** | MAF Mode | Flat Open Loop | `Open Loop EQ`, `IVT Gain`, `Injector Temp Gain` | Set all to **1.0** |
| **Step 4B** | VVE Mode | Force Speed Density | `High RPM Disable/Re-enable` | **8192 RPM** (9000 input) |
| **Step 4B** | VVE Mode | Fail MAF Sensor | `Engine Diag -> MAF Frequency Fail` | **0 Hz** |
| **Step 4B** | VVE Mode | Trigger SD Fallback | `Engine Diag -> DTCs (P0101, P0102, P0103)` | **Report on 1st Error** (DO NOT disable!) |
| **Step 4B** | VVE Mode | Disable DFCO | `Fuel -> Cutoff -> DFCO Enable Temp / RPM` | Temp = **256°C**, RPM = **9000 RPM** |
| **Step 4B** | VVE Mode | Calculate Coeffs | `Virtual VE Editor -> Calculate Coefficients` | **Mandatory** after editing VVE table! |
| **Step 4C** | Blended Mode | Restore Compare file | `Compare File -> Base ROM` | Restore DFCO, Closed Loop ECT, Dynamic Airflow |
| **Step 5** | WOT Fueling | Final PE Targets | `Fuel -> PE -> EQ Ratio Gas` | **1.12** @ 2500 RPM -> **1.163** @ 5250 RPM |
| **Step 5** | WOT Spark | High Octane Spark | `Spark -> Advance -> High Octane` | Advance in **+2° steps**, monitor dyno & KR |

---

## 5. Minimum Scanner Evidence per Logging Pass

Every tuning iteration logged in [docs/tuning-entry-template.md](file:///home/ls0775/source/repos/GMTuning/docs/tuning-entry-template.md) must record:
- **Airflow Parameters:** RPM, MAP (kPa), MAF Hz, Dynamic Airflow (g/s), Cylinder Air Mass (g/cyl).
- **Fueling Parameters:** STFT Bank 1/2 (%), Commanded EQ Ratio (`[50118.238]`), Measured Wideband Lambda (`[50119.238]`), Injector Pulse Width (ms).
- **Ignition Parameters:** Final Spark Advance (°), Knock Retard (°).
- **Thermal Conditions:** Engine Coolant Temperature (ECT °C), Intake Air Temperature (IAT °C).

---

## 6. Hard Stop Conditions

Immediately abort dyno/road run if any of the following occur:
1. **Repeatable Knock Retard (KR) > 2.0°** under wide open throttle.
2. **Lean WOT Trend:** Measured Lambda > 0.90 ($>13.2\text{ AFR}$) during Power Enrichment pull.
3. **Thermal Excursion:** ECT > 105°C or IAT > 50°C during calibration runs.
4. **Unexpected DTCs:** Any unexpected misfire, O2 sensor failure, or CAN communication DTC.
