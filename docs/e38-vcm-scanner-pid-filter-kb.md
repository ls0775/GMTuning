# E38 VCM Scanner Numeric Token KB (`[PID.Unit]`)

Built from your files:

- `HP Academy SD Patch.Layout.xml`
- `HP Academy SD Patch.Graphs.xml`
- `HP Academy SD Patch.Channels.xml`
- `VE SS Worked Example.Channels.xml`
- all provided `*.MathParameter.xml`

This now uses the exact Scanner token style you asked for, e.g. **`[50118.238]`**.

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

## 3) Graph set and copy/paste filters (numeric tokens)

Create these 5 separate histograms in VCM Scanner:

1. MAF CL
2. MAF PE
3. VVE CL
4. VVE PE
5. Mixed Validation

### 1) MAF CL filter (MAF-only mode)

```text
([50080.50] > 2499) and ([50080.50] < 7201) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50090.156] > 10) and ([50070.56.slope(50)] < 100 and [50070.56.slope(50)] > -100) and ([50090.156.slope(100)] < 1 and [50090.156.slope(100)] > -1)
```

### 2) MAF PE filter (MAF-only mode)

```text
([50080.50] > 5199) and ([50118.238] > 1.09) and ([50119.238] > 0.74) and ([50119.238] < 1.26) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 55) and ([50090.156] > 84)
```

### 3) VVE CL filter (SD/VVE-only mode)

```text
([50070.56] > 999) and ([50070.56] < 4001) and ([50030.91] > 24) and ([50030.91] < 101) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50020.113] > 19) and ([50090.156] > 2) and ([50070.56.slope(50)] < 100 and [50070.56.slope(50)] > -100) and ([50090.156.slope(100)] < 1 and [50090.156.slope(100)] > -1)
```

### 4) VVE PE filter (SD/VVE-only mode)

```text
([50070.56] > 1199) and ([50070.56] < 4201) and ([50030.91] > 84) and ([50118.238] > 1.09) and ([50119.238] > 0.74) and ([50119.238] < 1.26) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 55) and ([50090.156] > 84)
```

### 5) Mixed Validation filter (blended mode)

```text
([50070.56] > 1199) and ([50070.56] < 3001) and ([50030.91] > 29) and ([50030.91] < 76) and ([50118.238] > 0.989) and ([50118.238] < 1.011) and ([50119.238] > 0.90) and ([50119.238] < 1.10) and ([50111.161] < 0.1) and ([50010.241] > 79) and ([50010.241] < 106) and ([50011.241] < 50) and ([50020.113] > 49) and ([50090.156] > 1) and ([50090.156] < 36)
```

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
