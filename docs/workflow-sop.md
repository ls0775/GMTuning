# E38 L98 Tuning Workflow SOP

## Scope

Repeatable process for safe reflash tuning with HP Tuners.

## Order of Operations

1. Baseline log and health checks
2. MAF calibration
3. VE (virtual VE coefficients / dynamic airflow strategy)
4. PE/WOT fueling
5. Spark optimization (with KR control)
6. Torque management and shift behavior

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
