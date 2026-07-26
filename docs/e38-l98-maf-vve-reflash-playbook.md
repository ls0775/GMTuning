# E38 L98 Reflash Playbook (MAF Rescale + VVE Calibration)

Derived from your 7 transcript files and adapted to your vehicle strategy:

- Vehicle platform: 2007 Holden Commodore VE V8
- Engine/PCM: Gen4 L98 with E38 PCM
- Transmission/diff: 6L80E, 2.92
- Hardware example: 1-7/8" headers, dual 2.5" exhaust, Crow 871286 cam + supporting mods
- Preferred method: **HP Tuners GM Gen III/IV LS - MAF Rescale / VVE Calibration**

## Step 0 - Introduction (Method Selection)

**Objective:** Confirm tuning method and expected workflow length.

**Method for this project:** Keep factory blended airflow model, calibrate both MAF and VVE, then return to blended operation.

**Why:** E38 uses both MAF and VVE calculations; tuning both gives better drivability and transient behavior than tuning one side only.

## Step 1 - Downloading Stock ROM

**Objective:** Capture an untouched rollback file and create a working copy.

1. Read ECM/TCM with VCM Editor (as required).
2. Save base file with a clear naming convention.
3. Immediately Save As a working file name (do not overwrite stock base).
4. Record file names and checksums in `docs/vehicle-baseline.md`.

**Exit criteria:**
- Base ROM preserved and immutable.
- Working ROM created for all edits.

## Step 2 - Modifications Capture (Required)

**Objective:** Define hardware scope before touching calibration.

Capture at minimum:

1. Make/model/year, engine code, PCM
2. Transmission/converter, diff ratio, tyre size
3. Intake/MAF hardware, injector details
4. Exhaust/header/cat status
5. Camshaft specs + supporting valvetrain mods
6. Fuel system and fuel type
7. Emissions hardware changes and related DTC implications

**Current project baseline:**
- 2007 Holden Commodore VE V8, L98, E38
- 6L80E auto, 2.92 diff
- 1-7/8" XForce headers, dual 2.5" exhaust
- Crow Cams 871286 with supporting mods

## Step 3 - Configure Base Tune File

**Objective:** Set a stable calibration state for airflow scaling and safe dyno/road work.

Typical setup actions (apply as relevant to your build):

1. Torque management review for tuning consistency.
2. Knock strategy setup (keep normal knock control active; adjust burst/decay behavior only if intentional).
3. Power Enrichment setup:
   - Set clear PE enable behavior.
   - Use a single temporary commanded lambda target while scaling airflow.
4. Temporarily disable LTFT carry effects as needed for cleaner calibration feedback.
5. Review DTC behavior for known hardware changes (cats/O2/MAF-related only as needed).

**Guardrail:** These are setup changes for calibration clarity, not permanent blanket disables.

## Step 4 - Air and Fuel Scaling (Core of this workflow)

### 4A. MAF-only calibration pass

**Objective:** Correct MAF transfer function first.

1. Force operation to reference MAF side for calibration pass.
2. Use wideband-based equivalence/lambda error histogram versus **MAF frequency**.
3. Collect smooth steady-state data up to mid/high MAF frequency.
4. Collect WOT ramp data for higher-frequency cells.
5. Apply corrections iteratively while preserving smooth curve shape.

**Targets:**
- Realistic calibration error band: around +/-1% in tuned regions.
- Prefer slight rich bias over slight lean bias when uncertain.

### 4B. VVE/SD calibration pass

**Objective:** Correct virtual VE model after MAF is dialed.

1. Configure ECU to ignore MAF input and run SD/VVE for this pass.
2. Build wideband-based histogram using RPM vs MAP axes aligned to VVE breakpoints.
3. Tune steady-state low/mid load areas, then WOT transition/high load areas near crossover.
4. Apply edits in VVE Editor, calculate coefficients each cycle.
5. Extrapolate smooth trends into cells that cannot be directly hit.
6. Copy tuned VVE mode into other VE modes where appropriate for your non-DOD/non-IMRC setup.

### 4C. Return to blended operation

**Objective:** Restore normal E38 operating strategy with your new MAF+VVE data.

1. Revert temporary setup tables from base compare file.
2. Restore dynamic airflow thresholds and MAF diagnostics settings.
3. Keep tuned MAF and VE coefficients.

**Exit criteria for Step 4:**
- MAF and VVE both calibrated with low, consistent error.
- Blended mode restored without temporary tuning overrides left behind.

## Step 5 - Optimising the Tune

**Objective:** Finalize WOT fueling and spark safely.

1. Set final PE lambda/EQ targets for your combination.
2. Verify measured lambda tracks commanded closely through the pull.
3. Tune high-octane spark by load/RPM zone:
   - Add timing in controlled increments.
   - Track torque/power response and KR behavior.
   - Remove timing in repeatable knock zones.
4. Keep table shape smooth (avoid abrupt cell cliffs).

**Rule:** Prioritize repeatable knock-free operation over marginal peak gains.

## Step 6 - Confirm Calibration on the Road

**Objective:** Validate dyno calibration under real airflow, temperature, and transient conditions.

1. Cruise validation:
   - Stable temperatures first (ECT/IAT).
   - Review STFT (and combined trims if LTFT retained).
   - Practical cruise trim goal: typically within about +/-5%.
2. WOT road/track validation:
   - Use high-load gears where safely possible.
   - Confirm lambda and KR behavior match dyno expectation.
3. Transient validation:
   - Sharp throttle in/out, shifts, and reapplication zones.
   - Confirm crisp response without bogging or repeatable knock.

**Pass criteria:**
- No repeatable KR hotspots.
- Commanded vs measured fueling is controlled in cruise and WOT.
- Drivability is consistent in real-world use.

## Session Execution Rules

1. Change one subsystem at a time.
2. Log before and after each flash.
3. Record exact table paths and range edits in `templates/tuning-entry-template.md`.
4. Keep a known-good rollback file at each milestone.
5. If in doubt, bias safer and iterate.
