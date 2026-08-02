# E38 VCM Scanner PID & Filter Knowledge Base (Modernized)

Complete reference for **HP Tuners VCM Scanner** logging, PID tokens, math parameters, and filter expressions for **GM E38 PCM (Gen IV LS3 / L98 V8)**. Designed for consistent, high-quality road and dyno data logging in both **Closed-Loop (CL)** and **Open-Loop (OL)** modes.

---

## 1. Core Rule: LTFT Disable Strategy & Rationale (Transcript-Aligned)

> [!IMPORTANT]
> **Why are Long Term Fuel Trims (LTFTs) Disabled in E38 Reflash Tuning?**
>
> On GM E38 PCMs, **LTFT behavior in Open Loop (PE / WOT) is asymmetric**:
> 1. **Positive LTFTs ($>0\%$):** If the PCM learns a positive trim in closed loop, it **carries over into Open Loop / Power Enrichment (WOT)**, adding uncommanded extra fuel at WOT.
> 2. **Negative LTFTs ($<0\%$):** If the PCM learns a negative trim, it is **ignored** in Open Loop / WOT.
>
> **Project & Transcripts Rule:**
> - **LTFTs are explicitly DISABLED** in the tune (`Engine -> Fuel -> Open & Closed Loop -> LTFT Enable Min ECT = 256°C`, `Max ECT = -40°C`).
> - **Short Term Fuel Trims (STFTs) are RETAINED** for closed-loop cruise feedback because STFTs provide instantaneous correction without ever carrying over into Open Loop / WOT.
> - **Road Cruise Logging:** Uses **STFT Only** (Bank 1 / Bank 2) as the primary closed-loop feedback metric.
> - **Optional Reference:** If analyzing a stock ROM where LTFTs were retained, the combined trim math formula (`STFT + LTFT`) is used.

---

## 2. Rule 0: Fueling Units Consistency (Lambda Only)

To prevent severe calibration errors, **never mix Air-Fuel Ratio (AFR) and Lambda ($\lambda$) / Equivalence Ratio (EQ) units** in the same VCM Scanner layout or filter setup.

- **Project Standard:** **Equivalence Ratio / Lambda ($\lambda$) Only**.
- **Equivalence Ratio ($EQ$):** $EQ = \frac{\text{Stoich AFR}}{\text{Actual AFR}} = \frac{1}{\lambda}$
- **At Stoichiometric Target (Closed Loop):**
  $$\text{Commanded EQ } [50118.238] = 1.00 \quad (\lambda = 1.00)$$
- **Under Power Enrichment Target (Open Loop WOT):**
  $$\text{Commanded EQ } [50118.238] = 1.174 \quad (\lambda = 0.85 \approx 12.5:1 \text{ AFR on 14.67 stoich})$$

---

## 3. Physical Transport Delay & Wideband Tailpipe Sniffer Calibration

> [!WARNING]
> **Understanding & Adjusting Wideband Transport Delay (`.shift(ms)`)**
>
> When using a wideband sensor mounted in a **tailpipe sniffer** (at the rear of the exhaust system):
> 1. **Physical Distance & Gas Velocity:** Exhaust gases take time to travel down the primary headers, high-flow cats, dual 2.5" cat-back piping, mufflers, and tailpipe adapter to reach the sensor tip.
> 2. **Variable Lag:** This delay is **NOT fixed at 800 ms**. It varies based on engine RPM, exhaust gas velocity, exhaust length, and wideband sensor response time:
>    - At low RPM / tip-in: Delay can be **$1000\text{--}1400\text{ ms}$**.
>    - At high RPM / 6000+ WOT pull: Delay can shrink to **$400\text{--}600\text{ ms}$**.
> 3. **Risk of False Lean Corrections:** If the delay filter is too short, the initial transient lean spike (as exhaust gas travels down the pipe) will pollute steady-state WOT histograms. The tuner will falsely see a "lean" cell and add fuel to WOT cells that are already correctly calibrated, causing over-enrichment!

### How the Tuner Measures & Adjusts the Delay Offset (`.shift(X)`)

1. **Open VCM Scanner Chart View** for a logged WOT pull.
2. **Find Pedal Step Timestamp ($T_{\text{pedal}}$):** Note the exact timestamp where `Accelerator Pedal Position [76.156]` crosses $>80\%$.
3. **Find Wideband Settling Timestamp ($T_{\text{WB}}$):** Note the timestamp where `Wideband Lambda [50119.238]` drops and stabilizes at WOT target (e.g. $0.85\lambda$).
4. **Calculate Measured Lag ($\Delta T$):**
   $$\Delta T = T_{\text{WB}} - T_{\text{pedal}} \quad (\text{in milliseconds})$$
5. **Update Filter String:** Replace `.shift(800)` in your VCM Scanner filter expression with `.shift(\Delta T)` (e.g. `.shift(1200)` for low-RPM tailpipe sniffer pulls or `.shift(600)` for front-collector bungs).
6. **Verify Histogram Output:** Check that the histogram excludes the initial transient lean spike and populates only clean, steady-state WOT Lambda data.

---

## 4. Master E38 PID & Channel Mapping Table

This table maps VCM Scanner parameter names, PID tokens, engineering units, and primary tuning applications for the GM E38 ECM and 6L80E TCM.

| Parameter Name | Channel Name | PID Token | Units | Primary Tuning Application |
|---|---|---|---|---|
| **Engine Speed** | Engine Speed | `[50070.56]` | RPM | Primary X-axis for VE, spark, & PE tables |
| **Manifold Pressure** | Manifold Absolute Pressure | `[50030.91]` | kPa | Load Y-axis for VVE tables & fuel mode cutovers |
| **Barometric Pressure** | Baro Pressure | `[50031.91]` | kPa | Ambient pressure correction baseline |
| **MAF Frequency** | Mass Air Flow Frequency | `[50080.50]` | Hz | X-axis for MAF Calibration curve (2700–12000+ Hz) |
| **MAF Airflow** | Mass Air Flow | `[50040.71]` | g/s | Direct mass airflow measurement from sensor |
| **Dynamic Airflow** | Dynamic Airflow | `[2320.71]` | g/s | ECU calculated airflow source (blended MAF/SD) |
| **VVE Airflow** | Calculated VE Airflow | `[2311.71]` | g/s | Speed density calculated airflow from VVE model |
| **Cylinder Air Mass** | Air Mass / Airmass | `[2321.56]` | g/cyl | Y-axis load for Spark Advance & Knock Retard maps |
| **Vehicle Speed** | Vehicle Speed | `[50020.113]` | km/h | Road speed & transmission gear validation |
| **Throttle Position** | Throttle Position (SAE) | `[50090.156]` | % | Throttle plate position for PE entry & transient filters |
| **Accelerator Pedal** | Accelerator Pedal Position | `[76.156]` | % | Driver pedal input for PE entry & tip-in filters |
| **Engine Coolant Temp** | Engine Coolant Temp | `[50010.241]` | °C | Thermal filter baseline (validates 80–105°C range) |
| **Intake Air Temp** | Intake Air Temp | `[50011.241]` | °C | Air density filter baseline (validates < 50°C window) |
| **Intake Valve Temp** | Intake Valve Temp (IVT) | `[2127.241]` | °C | Fuel charge temperature compensation |
| **Commanded Lambda** | Equivalence Ratio Commanded | `[50118.238]` | EQ ($\lambda^{-1}$) | ECU commanded EQ ratio target ($1.00 = \text{Stoich}$) |
| **Wideband Lambda** | WB EQ Ratio 1 / Lambda | `[50119.238]` | $\lambda$ | Measured exhaust Equivalence Ratio / Wideband Lambda |
| **Short Term Trim B1** | Short Term Fuel Trim Bank 1 | `[50156.156]` | % | Closed-loop immediate feedback correction Bank 1 (Active) |
| **Short Term Trim B2** | Short Term Fuel Trim Bank 2 | `[50158.156]` | % | Closed-loop immediate feedback correction Bank 2 (Active) |
| **Long Term Trim B1** | Long Term Fuel Trim Bank 1 | `[50155.156]` | % | Disabled in tune; reference only for stock baseline |
| **Long Term Trim B2** | Long Term Fuel Trim Bank 2 | `[50157.156]` | % | Disabled in tune; reference only for stock baseline |
| **Spark Advance** | Total Spark Advance | `[50110.161]` | Deg (°) | Actual delivered ignition timing |
| **Knock Retard** | Knock Retard | `[50111.161]` | Deg (°) | ECU timing retard in response to detonation |
| **Burst Knock Retard** | Burst Knock Retard | `[2120.161]` | Deg (°) | Preemptive timing retard on rapid throttle delta |
| **Injector Pulse Width B1**| Injector Pulse Width Bank 1 | `[50151.254]` | ms | Fuel injector duration Bank 1 |
| **Injector Pulse Width B2**| Injector Pulse Width Bank 2 | `[50152.254]` | ms | Fuel injector duration Bank 2 |
| **Current Gear** | Trans Current Gear | `[6001.1]` | Gear | 6L80E current gear state (1–6) |

---

## 5. Road Logging Workflows

### A) Closed-Loop (CL) Road Logging Strategy (STFT Cruise Trimming)
- **Objective:** Gather steady-state STFT fuel trim data during normal street cruising to confirm cruise airflow calibration without LTFT carry-over contamination.
- **Preconditions:**
  - **LTFTs Disabled** in PCM (`Min ECT = 256°C`, `Max ECT = -40°C`).
  - STFTs active for real-time closed-loop correction.
  - Engine fully warm ($\text{ECT} = 85\text{--}95^\circ\text{C}$).
  - DFCO active (filtered out in Scanner histograms).
- **Driving Technique:**
  - Drive in 3rd or 4th gear at steady road speeds (60 km/h, 80 km/h, 100 km/h).
  - Apply slow, gradual throttle inputs; avoid sharp stabs or sudden lifts.
  - Collect 15–30 minutes of continuous road logging to accumulate $\ge 50\text{--}100+$ hits per cell.
- **Histogram Target:** Short Term Fuel Trim (STFT) within **$\pm 5\%$** (ideally near $0\%$).

### B) Open-Loop (OL) / Wideband Road Logging Strategy (WOT & Air Model Rescaling)
- **Objective:** Calibrate MAF frequency curve and VVE map accurately using wideband measured Lambda error.
- **Preconditions:**
  - STFTs disabled during open-loop calibration passes (`Closed Loop Enable ECT = 256°C`).
  - Commanded EQ forced flat to $1.00$ for cruise scaling or set to PE target ($1.174$) for WOT pulls.
- **Driving Technique:**
  - **MAF / VVE Cruise Scaling:** Steady-state dyno hold or smooth road acceleration in high gear.
  - **WOT Ramp Pulls:** 3rd or 4th gear pull from 2000 RPM up to redline.
  - **Transport Delay Filter:** Use `.shift(\Delta T)` filter (e.g. `.shift(800)` to `.shift(1200)`) to ignore the measured transport delay after tip-in, excluding transient lean lag from corrupting steady-state WOT data.
- **Histogram Target:** Wideband EQ Error % within **$\pm 1\%$**.

---

## 6. Modern Filter Catalog (Copy/Paste Expressions)

### Category A: MAF Rescaling Filters

#### A1 — MAF Closed-Loop STFT Steady-State Filter
Suppresses throttle transients, deceleration overrun, cold engine conditions, and knock events during MAF cruise calibration:

```text
([50080.50] > 2499) and ([50080.50] < 7201) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50090.156] > 8) and ([50070.56.slope(50)] < 100 and [50070.56.slope(50)] > -100) and ([50090.156.slope(100)] < 1 and [50090.156.slope(100)] > -1)
```

#### A2 — MAF Power Enrichment (WOT Calibration Filter — Adjustable `.shift(X)` Delay)
Isolates WOT MAF operation and ignores the measured transport delay (adjust `.shift(800)` to your measured $\Delta T$ ms offset):

```text
([50118.238] < 0.90) and ([50119.238] < 1.25) and ([50011.241] < 55) and ([76.156.shift(800)] > 80) and ([76.156] > 80) and ([50111.161] < 0.1)
```

---

### Category B: Virtual VE (VVE / Speed Density) Filters

#### B1 — VVE Closed-Loop STFT Steady-State Filter
Ensures pristine data quality for RPM vs MAP cells during Speed Density calibration passes:

```text
([50070.56] > 999) and ([50070.56] < 4001) and ([50030.91] > 24) and ([50030.91] < 101) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50020.113] > 19) and ([50090.156] > 2) and ([50070.56.slope(50)] < 100 and [50070.56.slope(50)] > -100) and ([50090.156.slope(100)] < 1 and [50090.156.slope(100)] > -1)
```

#### B2 — VVE Power Enrichment Filter (High Load SD Pass — Adjustable `.shift(X)` Delay)
Filters VVE data under WOT load while suppressing transport lag and gearshift/tip-in spikes (adjust `.shift(800)` to measured $\Delta T$):

```text
([50118.238] < 0.88) and ([50030.91] > 85) and ([50011.241] < 55) and ([50119.238] < 1.25) and ([76.156.shift(800)] > 80) and ([76.156] > 80) and ([50111.161] < 0.1)
```

---

### Category C: Transient & Tip-In Isolation Filters

#### C1 — Transient Tip-In Lean Spike Isolation Filter
Isolates the initial tip-in window ($>80\%$ pedal) to analyze transient fueling lag separately from steady-state air models:

```text
([50118.238] < 0.95) and ([50011.241] < 55) and ([76.156] > 80) and ([76.156.shift(700)] < 80)
```

---

### Category D: Mixed-Mode Real World Validation Filters

#### D1 — Blended Mode Road Cruise STFT Validation
Validates Short Term Fuel Trims under real-world street cruise conditions (MAF + VVE active):

```text
([50070.56] > 1199) and ([50070.56] < 3001) and ([50030.91] > 29) and ([50030.91] < 76) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50020.113] > 49) and ([50090.156] > 1) and ([50090.156] < 36)
```

#### D2 — Blended Mode WOT Road Knock & Lambda Validation
Checks real-world WOT fueling tracking and knock retard in 3rd/4th gear pulls:

```text
([50118.238] < 0.90) and ([50119.238] < 1.25) and ([50011.241] < 55) and ([76.156] > 80) and ([50111.161] < 0.1)
```

---

## 7. Confirmed Math Channel Definitions & Formulas

Use these formulas when setting up VCM Scanner custom Math Parameters (`Tools -> Math Parameters`):

### 1. Equivalence Ratio Error % (Lambda Error)
Calculates percentage error between measured wideband lambda and commanded EQ ratio target:

$$\text{EQ Error \%} = \frac{\text{WB Lambda} - \text{Cmd Lambda}}{\text{Cmd Lambda}} \times 100$$

**VCM Scanner Formula:**
```text
([50119.238] - [50118.238]) / [50118.238] * 100
```

---

### 2. Combined Fuel Trim % (STFT + LTFT) — Stock Reference Only
Used ONLY when analyzing an un-tuned stock ROM where LTFTs were retained:

$$\text{Combined Trim \%} = \text{STFT Bank 1} + \text{LTFT Bank 1}$$

**VCM Scanner Formula:**
```text
[50156.156] + [50155.156]
```

---

### 3. MAF Airflow Error % (Lambda Method)
Calculates percentage error between Dynamic Airflow model and direct MAF measurement:

**VCM Scanner Formula:**
```text
(([2320.71] + ([2320.71] * ([50119.238] - [50118.238]) / [50118.238])) - [50040.71]) / [50040.71] * 100
```

---

### 4. VVE Airflow Error % (Lambda Method)
Calculates percentage error between Dynamic Airflow model and Virtual VE calculated airflow:

**VCM Scanner Formula:**
```text
(([2320.71] + ([2320.71] * ([50119.238] - [50118.238]) / [50118.238])) - [2311.71]) / [2311.71] * 100
```

---

## 8. Histogram Setup Quick Reference Guide

| Graph / Histogram Name | Parameter Plotted | X-Axis (Columns) | Y-Axis (Rows) | Copy Axis Breakpoints From VCM Editor |
|---|---|---|---|---|
| **MAF EQ Error %** | Wideband EQ Error % | MAF Frequency (`[50080.50]`) | N/A | `Engine -> Airflow -> MAF Calibration` |
| **VVE EQ Error %** | Wideband EQ Error % | Engine Speed (`[50070.56]`) | MAP kPa (`[50030.91]`) | `Edit -> Virtual Volumetric Efficiency` |
| **STFT Cruise %** | Short Term Fuel Trim B1 | Engine Speed (`[50070.56]`) | MAP kPa (`[50030.91]`) | `Edit -> Virtual Volumetric Efficiency` |
| **Spark Advance Map** | Total Spark Advance (°) | Engine Speed (`[50070.56]`) | Air Mass (`[2321.56]`) | `Engine -> Spark -> High Octane` |
| **Knock Retard Map** | Knock Retard (°) | Engine Speed (`[50070.56]`) | Air Mass (`[2321.56]`) | `Engine -> Spark -> High Octane` |
