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

## First Steps

1. Fill out `docs/vehicle-baseline.md`.
2. Capture a clean baseline log and record it with `templates/tuning-entry-template.md`.
3. Create your first session entry under `logs/` using the template.
