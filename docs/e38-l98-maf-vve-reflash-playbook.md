# E38 L98 Reflash Playbook (MAF Rescale + VVE Calibration)

Detailed, transcript-derived operating playbook for performance tuning a **2007 Holden Commodore VE V8 (Gen4 L98 engine, E38 PCM, 6L80E transmission)** using HP Tuners VCM Editor and VCM Scanner.

---

## Vehicle & Project Baseline

- **Platform:** 2007 Holden Commodore VE V8
- **Engine / PCM:** Gen4 L98 (6.0L / 6.2L LS architecture) with E38 ECM
- **Transmission / Diff:** 6L80E 6-speed automatic, 2.92 ratio differential
- **Hardware Modifications:** X-Air Over-The-Radiator (OTR) Cold Air Intake, 1-7/8" XForce headers, dual 2.5" exhaust system, Crow Cams 871286 camshaft with supporting valvetrain upgrades
- **Airflow Strategy:** Factory Blended Airflow (MAF + Virtual Volumetric Efficiency / Speed Density)

---

## Step 0 - Introduction & Airflow Strategy Selection

### Objective
Establish the tuning framework and confirm the primary airflow strategy.

### Airflow Operating Model
The GM E38 PCM uses a dual/blended airflow calculation:
1. **Mass Air Flow (MAF):** Directly measures mass airflow in g/s via frequency (Hz). Primary source at high RPM (> 4000 RPM) and steady-state cruise.
2. **Speed Density / Virtual Volumetric Efficiency (VVE):** Calculates mass airflow dynamically from MAP (kPa), RPM, and IAT. Primary source during transient throttle tip-in and low RPM operating modes.

### Why Calibrate Both?
Tuning both MAF and VVE ensures smooth transient response, crisp tip-in, factory-level drivability, and precise fueling control across all load conditions.

---

## Step 1 - Downloading & Preserving Stock ROM

### Objective
Create an untouched, immutable baseline file and establish working file conventions.

### Execution Procedure
1. Turn vehicle ignition ON (engine OFF). Connect HP Tuners interface to OBD-II port and laptop.
2. Open **VCM Editor** and click **Read Vehicle**. Select ECM (E38) and TCM (6L80E).
3. Once read complete, save baseline file with standard naming format:
   - `VE_R8_Clubsport_Stock_Base.hpt`
4. Immediately select **Save As** to create a working copy:
   - `VE_R8_Clubsport_XAir_OTR.hpt`
5. Record OS ID, Calibration IDs, and baseline details in [vehicle-baseline.md](file:///home/ls0775/source/repos/GMTuning/docs/vehicle-baseline.md).

> [!IMPORTANT]
> Never overwrite the original stock `.hpt` file. Always use the Compare Function against `Stock_Base.hpt` to revert temporary setup tables.

---

## Step 2 - Modification Capture & Baseline Checklist

### Objective
Document all hardware changes to determine exact calibration requirements.

### Hardware Scope (Baseline Build)
- **Intake:** X-Air OTR Cold Air Intake (alters MAF duct geometry & velocity profile -> requires MAF rescaling).
- **Exhaust:** 1-7/8" long-tube headers into dual 2.5" cat-back (increases volumetric efficiency -> requires VVE calibration).
- **Valvetrain:** Crow Cams 871286 cam + valve springs (alters intake valve timing and idle vacuum -> requires idle & VVE adjustments).

---

## Step 3 - Base Tune File Configuration (VCM Editor Setup)

### Objective
Configure PCM limits, knock parameters, and fueling targets to prepare for safe dyno/road calibration.

### 1. Torque Management (`Engine -> Torque Management`)
- **Max Engine Torque:** Set torque values in each gear table to maximum allowed (e.g., 1000 Nm).
- **Transmission Input Max:** Set to maximum allowed value: **8192 Nm**.
- **Brake Torque Limit:** Increase numbers in `Brake Torque Limit` table to prevent throttle closure when brake-loading/launching.

### 2. Knock Strategy Setup (`Engine -> Spark -> Retard`)
- **Max Knock Retard (`Max Retard vs MAP vs RPM`):** Multiply entire table by **0.75** (reduces max allowable retard by 25%, e.g., capping max retard from 10° down to 8° above 1500 RPM).
- **Burst Knock Retard (`Base vs Cylinder Air Delta`):** Highlight entire table and set all values to **0** to eliminate false preemptive retard on transient throttle inputs.
- **Knock Retard Decay (`Knock Retard Decay`):** Highlight entire table and multiply by **2.0** to double the speed at which timing is restored after a knock event.

### 3. Power Enrichment Setup (`Engine -> Fuel -> Power Enrichment`)
- **PE Pedal Position (`PE Throttle Pedal`):**
  - Set 0–2500 RPM cells to **40%**.
  - Set 4500 RPM+ cells to **5%**.
  - Horizontally interpolate between 2500 and 4500 RPM.
- **Temporary PE EQ Target (`EQ Ratio Gas`):** Set entire table flat to **1.174** (corresponds to **0.85 Lambda** / **12.5:1 AFR** for 14.67 stoich).
  $$\text{EQ Ratio} = \frac{\text{Stoich AFR}}{\text{Target AFR}} = \frac{14.67}{12.5} = 1.174 \quad \left(\text{or } \frac{1}{\lambda} = \frac{1}{0.85} = 1.176\right)$$
- **Enrichment Ramp In Rate:** Set from default `0.1` to **1.0** for immediate PE entry.
- **PE Delay (`PE Delay RPM`):** Set to **0 RPM** (and 0 ms).

### 4. Long Term Fuel Trims (LTFT) Disable (`Engine -> Fuel -> Open & Closed Loop`)
- **LTFT Enable Min ECT:** Set to **256°C** (enter 300, auto-reverts to max 256).
- **LTFT Enable Max ECT:** Set to **-40°C**.
  *(Disables LTFT carry-over into open loop while keeping STFT active for cruise calibration).*

### 5. DTC Diagnostics (`Engine Diagnostics -> DTCs`)
- If catalytic converters are removed: Disable **P0420** and **P0430** (Cat System Efficiency Bank 1/2) and rear O2 DTCs.

---

## Step 4 - Air and Fuel Scaling (Core Calibration Pass)

---

### 4A. MAF-Only Calibration Pass

#### Objective
Rescale the Mass Air Flow sensor frequency curve to eliminate measurement errors caused by the OTR intake.

#### ECU Setup Parameters
1. **Force MAF Mode (`Engine -> Airflow -> Dynamic`):**
   - `High RPM Disable` = **400 RPM**
   - `High RPM Re-enable` = **300 RPM**
2. **Disable Closed Loop & STFTs (`Engine -> Fuel -> Open & Closed Loop`):**
   - `Closed Loop Enable ECT vs Startup ECT` = **256°C** (enter 300)
   - `O2 Readiness ECT` = **256°C**
3. **Flat Open Loop Targets:** Set `Open Loop EQ Multiplier`, `Intake Valve Temp (IVT) Gain`, and `Injector Temp Gain` tables to **1.0**.

#### VCM Scanner Histogram Configuration
- **Parameter:** Equivalence Ratio Error % (`[50119.238] vs [50118.238]`)
- **Axis:** MAF Frequency Hz (`[50080.50]`)
- **Breakpoints:** Copy directly from VCM Editor (`MAF Calibration -> Column Axis -> Copy Labels`).

#### Logging & Data Collection Procedure
1. Bring engine to stable operating temperature (ECT 90–95°C, IAT stable).
2. **Steady-State Logging (2700 Hz to 7200 Hz):**
   - Use dyno load control to hold steady RPM in 4th gear.
   - Smoothly sweep throttle to collect data in each MAF Hz cell.
   - Minimum **50 counts** per cell (target **200–250+ counts** for clean averaging).
3. **WOT Ramp Logging (7200 Hz to 10,000+ Hz):**
   - Perform full WOT ramp pull in 4th gear.
   - **Stop logging before lifting off throttle** to prevent decel/tip-in transients from corrupting WOT data.

#### Applying Edits in VCM Editor
- Open `Engine -> Airflow -> General -> MAF Calibration`.
- Use `Paste Special -> Multiply by %` (or `Multiply by % - Half` when close to target), or manually smooth curve trends to preserve natural exponential shape.
- **Target:** Calibration error within **±1%** across all Hz cells (prefer slight rich bias over lean).

---

### 4B. Virtual VE (VVE) / Speed Density Calibration Pass

#### Objective
Calibrate the E38 Virtual VE coefficient table with MAF disabled.

#### ECU Setup Parameters
1. **Force Speed Density Mode (`Engine -> Airflow -> Dynamic`):**
   - `High RPM Disable` = **8192 RPM** (enter 9000)
   - `High RPM Re-enable` = **8192 RPM** (enter 9000)
2. **Fail MAF Sensor (`Engine Diagnostics -> Airflow`):**
   - `MAF Frequency Fail` = **0 Hz**
3. **MAF DTC Configuration (`Engine Diagnostics -> DTCs`):**
   - Set MAF DTCs (**P0101, P0102, P0103**) to **Report on 1st Error**.
   > [!CRITICAL]
   > Do NOT set MAF DTCs to "No Error Reported". The PCM must register a MAF fault to trigger Speed Density fallback!
4. **Disable Deceleration Fuel Cutoff (DFCO) (`Engine -> Fuel -> Cutoff`):**
   - `DFCO Enable Temp` = **256°C**, `Disable Temp` = **-40°C**
   - `DFCO Enable RPM` = **9000 RPM**, `Disable RPM` = **0 RPM**

#### VCM Scanner Histogram Configuration
- **Parameter:** Equivalence Ratio Error %
- **Columns (X-Axis):** Engine RPM (`[50070.56]`)
- **Rows (Y-Axis):** MAP kPa (`[50030.91]`)
- **Breakpoints:** Copy directly from Virtual VE Editor (`Edit -> Virtual Volumetric Efficiency -> Copy Labels`).

#### Applying Edits & Coefficient Calculation
1. Open Virtual VE Editor (`Edit -> Virtual Volumetric Efficiency`).
2. Select **Manifold Switch Open** VE mode.
3. Apply wideband EQ error via `Paste Special -> Multiply by %`.
4. Apply **Polynomial Smooth** maximum **1 time** (over-smoothing distorts true engine VE requirements).
5. **MUST click `Calculate Coefficients`** to compile edited VE values into ECU math coefficients!
6. **Trend Extrapolation:** Manually copy trends into unreached cells (low MAP vacuum <23 kPa and low RPM / high load cells).
7. **Copy to All Modes:** Copy tuned VE table into `Manifold Switch Closed`, `Displacement on Demand`, and `Manifold Switch Open` so all 4 VE modes match.

---

### 4C. Restore Factory Blended Airflow Mode

#### Objective
Return ECU to factory blended MAF + VVE operation with calibrated data.

#### Execution Procedure
1. Open stock baseline ROM (`Stock_Base.hpt`) using **Compare File**.
2. Copy back original settings for:
   - Dynamic Airflow thresholds (**4000 RPM Disable / 3900 RPM Re-enable**)
   - MAF Frequency Fail (**14500 Hz High / 300 Hz Low**)
   - MAF DTCs, DFCO settings, Closed Loop ECT enable tables, Open Loop EQ multipliers, IVT Gain, Injector Temp Gain.
3. **Retain:** Calibrated MAF frequency table and calculated VVE Coefficients.

---

## Step 5 - Optimising Fueling & Ignition Spark

### Objective
Finalize WOT Power Enrichment lambda targets and optimize High Octane spark advance.

### 1. Final Power Enrichment Fueling Targets (`Engine -> Fuel -> Power Enrichment`)
Configure final commanded EQ Ratio curve:
- **Low RPM (0–2500 RPM):** Set EQ to **1.12** ($\approx 0.89\lambda$ / 13.1:1 AFR).
- **High RPM (5250+ RPM):** Set EQ to **1.163** ($\approx 0.86\lambda$ / 12.6:1 AFR).
- **Mid-Range (2500–5250 RPM):** Horizontally interpolate between 2500 and 5250 RPM.
- *Verification:* Perform WOT dyno pull and verify wideband measured lambda tracks commanded lambda within **±1%**.

### 2. Spark Advance Optimization (`Engine -> Spark -> Advance -> High Octane`)
1. Identify operating load range in scanner histogram (typically **0.60 to 0.84 g/cyl airmass** under WOT).
2. Advance timing in **+2° increments** across the WOT airmass rows.
3. Perform dyno pull and compare torque/power curve overlay against previous run:
   - **Power Increases:** Timing was retarded; retain advance or test further.
   - **No Power Increase:** Engine is at/past Minimum Advance for Best Torque (**MBT**). **Remove added timing** (revert or retard 1–2°).
   - **Knock Retard (KR) Detected:** Immediately **retard timing** in affected load/RPM cells.
4. **IAT Spark Compensation Check:** Review `IAT Spark` compensation table (stock pulls 3° at 30°C IAT and 5° at 35°C IAT). Adjust threshold if dyno bay heat-soak causes artificial timing retard.

---

## Step 6 - Confirm Calibration on Road & Track

### Objective
Validate dyno calibration under real-world airflow, ambient temperatures, and transient driving conditions.

### 1. Cruise Trim Confirmation
- Drive vehicle under steady-state street conditions. Ensure ECT (88–95°C) and IAT are stable.
- Verify Short Term Fuel Trims (STFT) remain within **±5%** (ideally near 0%).

### 2. WOT Road / Track Pull
- Perform full WOT pull in high-load gear (3rd or 4th gear).
- Verify commanded vs measured wideband lambda stays within **±1%**.
- Verify zero repeatable Knock Retard (KR) events.

### 3. Transient & Drivability Validation
- Test sharp throttle tip-in from low RPM (**2200 RPM**) and mid RPM (**4000 RPM**).
- Perform full-throttle manual gear shifts.
- Check Scanner **Spark Retard Histogram**: verify table is clear of repeatable KR hits.
- Confirm crisp, immediate engine response without bogging, hesitation, or lean spikes.

---

## Summary SOP Checklist

| Step | Action | Key Parameters / Targets | Exit Criteria |
|---|---|---|---|
| **Step 1** | Download ROM | Save `Stock_Base.hpt` & `Working.hpt` | Immutable stock file preserved |
| **Step 2** | Modifications | Document intake, exhaust, cam specs | Hardware baseline frozen |
| **Step 3** | Base Tune Prep | Torque Max 8192Nm, KR Max *0.75, Burst KR=0, PE 40%/5%, Temp EQ=1.174, LTFT Disabled | Calibration prepped for open loop |
| **Step 4A** | MAF Rescale | Dyno hold 2700–7200Hz, WOT pull >7200Hz, EQ error vs MAF Hz | MAF error within **±1%** |
| **Step 4B** | VVE Calibration | MAF Fail=0Hz, MAF DTC 1st Error, EQ error vs RPM/MAP, Calc Coeffs | VVE error within **±1%**, Coeffs saved |
| **Step 4C** | Blended Mode | Restore Compare file defaults for DFCO, CL ECT, MAF Fail | Blended mode operational |
| **Step 5** | WOT & Spark | Final PE EQ 1.12–1.163, High Octane spark +2° steps, monitor MBT & KR | Clean power curve, 0 KR |
| **Step 6** | Road Validation | Cruise STFT, 3rd/4th gear WOT, transient tip-in check | Cruise STFT ±5%, 0 repeatable KR |
