# GMTuning Knowledge Base

Practical knowledge base for tuning a 2007 Holden Commodore VE (Gen4 L98, E38 PCM) using HP Tuners VCM Editor and VCM Scanner.

## Structure

- `docs/` - core references and procedures
- `logs/` - scanner logs and session artifacts
- `vcm-presets/` - VCM Scanner channel layouts and charts
- `templates/` - repeatable entry templates

## Operating Rules

1. Record one tuning subsystem at a time: MAF -> VE -> PE/WOT -> Spark -> Torque/Shift.
2. Link every change to a specific `.hpt` revision and scanner log.
3. Save rollback points before each major change.

## Course Framework Alignment

Transcript notes should map to this sequence:

1. Downloading Stock ROM
2. What Modifications Have Been Performed?
3. Configure Base Tune File
4. Air Model and Injector Characterization (MAF + Speed Density/MAP)
5. Optimising the Tune
6. Confirm Calibration on the Road

## First Steps

1. Fill out `docs/vehicle-baseline.md`.
2. Capture a clean baseline log and record it with `templates/tuning-entry-template.md`.
3. Create your first session entry under `logs/` using the template.

## Core Reference

Use `docs/e38-l98-maf-vve-reflash-playbook.md` as the transcript-derived operating playbook for this project.

For Scanner setup and clean-data filtering, use `docs/e38-vcm-scanner-pid-filter-kb.md`.
