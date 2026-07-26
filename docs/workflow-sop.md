# E38 L98 Tuning Workflow SOP

## Scope

Repeatable process for safe reflash tuning with HP Tuners.
Primary method for this project: **HP Tuners GM Gen III/IV LS - MAF Rescale / VVE Calibration**.

## Framework (Transcript-Aligned)

1. Download stock ROM and capture baseline log/health checks
2. Capture full modification set (Step 2)
3. Configure base tune file for the current hardware
4. Select airflow strategy and perform air model/injector characterization
5. Optimise fueling, spark, and torque behavior
6. Confirm calibration on road under real operating conditions

## Airflow Strategy Decision Tree (Step 4)

1. **Factory MAF present and reliable (preferred for street use)?**
   - Yes -> Use **MAF + VVE (standard E38 operating model)**.
   - No -> Go to question 2.
2. **MAF removed/unreliable but staying on factory-style VVE architecture?**
   - Yes -> Use **VVE-based Speed Density (MAP) tuning**.
   - No -> Go to question 3.
3. **Need full VE table workflow from a 1 Bar SD OS conversion?**
   - Yes -> Use **VE-based 1 Bar Speed Density OS**.
   - No -> Reassess hardware/sensor faults before tuning.

## Project Default Strategy (Current Vehicle)

- Default path: **MAF + VVE (standard E38)**.
- Escalate to SD-only paths only if hardware or use-case requires it.

## Step 2 Input Gate (Do Not Skip)

Before any calibration changes, capture and freeze:

1. Vehicle/engine/PCM/trans/diff
2. Intake/MAF/injector/fuel system
3. Exhaust/cat/O2 configuration
4. Camshaft and supporting hardware
5. Fuel type and expected operating conditions

If this data is incomplete, stop and complete Step 2 first.

## Practical Sub-Order Inside Step 4/5 (MAF + VVE Default)

1. MAF calibration
2. VE (virtual VE coefficients / dynamic airflow strategy)
3. PE/WOT fueling
4. Spark optimization (with KR control)
5. Torque management and shift behavior

## Session Rules

1. Change one subsystem per pass.
2. Keep change size conservative.
3. Log before and after each pass.
4. Record exact table paths and cell ranges changed.
5. Keep a known-good rollback file before each flash.

## Minimum Scanner Evidence per Pass

- RPM, MAP, MAF Hz
- STFT/LTFT B1/B2
- Commanded EQ and measured wideband AFR
- Spark advance and KR
- IAT, ECT, TPS, injector pulse width

## Stop Conditions

- Unexpected knock behavior
- Lean WOT trend
- Abnormal coolant/oil/engine behavior
- New persistent DTCs
