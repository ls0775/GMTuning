# E38 VCM Scanner Numeric Token KB (`[PID.Unit]`)

Built from your files:

- `HP Academy SD Patch.Layout.xml`
- `HP Academy SD Patch.Graphs.xml`
- `HP Academy SD Patch.Channels.xml`
- `VE SS Worked Example.Channels.xml`
- all provided `*.MathParameter.xml`

This now uses the exact Scanner token style you asked for, e.g. **`[50118.238]`**.

## Rule 0 - Fueling Units Consistency (Hard Rule)

Do not mix AFR-based and lambda-based filters/math in the same tuning workflow.

1. Choose one unit system per project.
2. Apply that same unit system to CL filters, PE filters, math channels, and validation charts.
3. If changing unit system, rebuild all dependent filters/math together before logging.

**Project rule for this repo:** use **lambda only**.

## 1) Confirmed token map (Name = token)

| Name | Token |
|---|---|
| RPM | `[50070.56]` |
| MAP kPa | `[50030.91]` |
| MAF g/s | `[50040.71]` |
| MAF Hz | `[50080.50]` |
| Vehicle speed | `[50020.113]` |
| ECT | `[50010.241]` |
| IAT | `[50011.241]` |
| TPS | `[50090.156]` |
| Spark advance | `[50110.161]` |
| KR | `[50111.161]` |
| EQ Cmd | `[50118.238]` |
| EQ (measured lambda/wideband path in this layout) | `[50119.238]` |
| LTFT B1 | `[50155.156]` |
| STFT B1 | `[50156.156]` |
| LTFT B2 | `[50157.156]` |
| STFT B2 | `[50158.156]` |
| Injector B1 pulse width | `[50151.254]` |
| Injector B2 pulse width | `[50152.254]` |
| Dynamic Airflow (math/source channel) | `[2320.71]` |
| VVE airflow channel used in math | `[2311.71]` |

## 2) Your explicit example (confirmed)

At stoich/closed-loop target:

```text
[50118.238] = 1
```

## 3) Filter catalog (one-line, cut/paste, mapped IDs)

Use separate histograms for each purpose. Pick the variant that matches current tuning objective.

### A) MAF CL (MAF modeling at stoich)

**A1 - strict steady-state (highest data quality):**

```text
([50080.50] > 2499) and ([50080.50] < 7201) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50090.156] > 10) and ([50070.56.slope(50)] < 100 and [50070.56.slope(50)] > -100) and ([50090.156.slope(100)] < 1 and [50090.156.slope(100)] > -1)
```

Why: best for clean MAF curve correction; heavily suppresses transients.

**A2 - moderate fill (more hits, slightly noisier):**

```text
([50080.50] > 2199) and ([50080.50] < 7601) and ([50118.238] > 0.985) and ([50118.238] < 1.015) and ([50111.161] < 0.3) and ([50010.241] > 75) and ([50010.241] < 110) and ([50011.241] < 55) and ([50090.156] > 6)
```

Why: use when strict filter leaves sparse cells.

### B) MAF PE (MAF modeling in PE)

**B1 - model-calibration PE (exclude early tip-in lean):**

```text
([50118.238] < 0.90) and ([50119.238] < 1.25) and ([50011.241] < 50) and ([76.156.shift(800)] > 80) and ([76.156] > 80) and ([50111.161] < 0.1)
```

Why: ignores first ~800 ms after tip-in so transient lean lag does not pollute MAF PE correction.

**B2 - transient-diagnosis PE (focus on tip-in event):**

```text
([50118.238] < 0.95) and ([50011.241] < 50) and ([76.156] > 80) and ([76.156.shift(700)] < 80)
```

Why: isolates CL->PE transition behavior; use to tune transient fueling separately from steady PE model.

### C) VVE CL (SD/VVE modeling at stoich)

**C1 - strict steady-state VVE CL:**

```text
([50070.56] > 999) and ([50070.56] < 4001) and ([50030.91] > 24) and ([50030.91] < 101) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50020.113] > 19) and ([50090.156] > 2) and ([50070.56.slope(50)] < 100 and [50070.56.slope(50)] > -100) and ([50090.156.slope(100)] < 1 and [50090.156.slope(100)] > -1)
```

Why: best VVE cell quality for SD calibration pass.

**C2 - moderate fill VVE CL:**

```text
([50070.56] > 899) and ([50070.56] < 4201) and ([50030.91] > 20) and ([50030.91] < 103) and ([50118.238] > 0.985) and ([50118.238] < 1.015) and ([50111.161] < 0.3) and ([50010.241] > 75) and ([50010.241] < 110) and ([50011.241] < 55)
```

Why: use when strict CL data is too sparse on road logs.

### D) VVE PE (SD/VVE modeling in PE)

**D1 - model-calibration PE (exclude early tip-in lean):**

```text
([50118.238] < 0.86) and ([50011.241] < 50) and ([50119.238] < 1.25) and ([76.156.shift(800)] > 80) and ([76.156] > 80) and ([50111.161] < 0.1)
```

Why: your preferred PE filter; protects VVE PE from the first ~700-800 ms lean transition.

**D2 - transient-diagnosis PE (capture tip-in lean only):**

```text
([50118.238] < 0.95) and ([50011.241] < 50) and ([76.156] > 80) and ([76.156.shift(700)] < 80)
```

Why: use to analyze and tune transient fueling strategy, not steady VVE table values.

### E) Mixed mode validation (MAF + VVE enabled)

**E1 - cruise validation:**

```text
([50070.56] > 1199) and ([50070.56] < 3001) and ([50030.91] > 29) and ([50030.91] < 76) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50020.113] > 49) and ([50090.156] > 1) and ([50090.156] < 36)
```

Why: confirms blended-mode drivability and trims after both models are calibrated.

**E2 - WOT validation:**

```text
([50118.238] < 0.90) and ([50119.238] < 1.25) and ([50011.241] < 55) and ([76.156] > 80) and ([50111.161] < 0.1)
```

Why: checks real-world WOT fueling/knock in blended mode without forcing MAF-only or SD-only.

## 4) Confirmed math channel definitions from your files

### MAF PE (lambda method)

```text
(([2320.71]+([2320.71]*([50119.238]-[50118.238])/[50118.238]))-[50040.71])/[50040.71]*100
```

### VVE PE (lambda method)

```text
(([2320.71]+([2320.71]*([50119.238]-[50118.238])/[50118.238]))-[2311.71])/[2311.71]*100
```

### MAF CL

```text
(([2320.71]+([2320.71]*([50116.156]+[50114.156])/100))-[50040.71])/[50040.71]*100
```

### VVE CL

```text
(([2320.71]+([2320.71]*([50116.156]+[50114.156])/100))-[2311.71])/[2311.71]*100
```

## 5) Remaining unresolved tokens

These appear in your AFR-based math files but are not labeled in the provided layout/channels:

- `[50120]`
- `[50121]`

Keep using the lambda pair (`[50118.238]`, `[50119.238]`) until those two are explicitly identified in Scanner.
