# Innovate LC-1 Wideband Free Air & Heater Calibration SOP

Complete operating guide for calibrating the **Innovate Motorsports LC-1 Digital Wideband Controller** and correcting ground offset errors in **VCM Scanner**.

---

## 1. When to Perform Free Air Calibration

Perform the LC-1 Free Air Calibration under any of the following conditions:
1. **First-time installation** of a new oxygen sensor or LC-1 controller.
2. **Wideband drift detected:** Log shows wideband reading artificially LEAN ($>1.10\lambda$) while factory narrowband O2 sensors read RICH ($>0.75\text{V}$).
3. **Every 3 to 6 months** (or 10,000 km) of regular vehicle operation.
4. **After severe engine misfire or rich fouling events.**

---

## 2. Safety & Preparation Rules

> [!CRITICAL]
> **100% Clean Ambient Air Required!**
> Do NOT attempt free air calibration while the sensor is installed in an exhaust pipe if the engine has been run recently. Residual unburned fuel or exhaust gases trapped in the pipe will corrupt the $20.9\%\text{ O}_2$ reference baseline.
>
> **Best Practice:** Unthread the wideband O2 sensor from the tailpipe/exhaust bung completely and suspend it in open, fresh ambient air outside the vehicle.

---

## 3. Step-by-Step Calibration Procedure

### Phase 1: Controller Sensor Reset (Heater Reset)
1. Turn vehicle ignition **OFF**.
2. **Disconnect the 6-pin sensor connector** from the LC-1 controller unit.
3. Turn ignition **ON** (Engine OFF). Wait **20 seconds**.
   - *Behavior:* The LC-1 status LED will flash error code `2` (No sensor connected).
4. Turn ignition **OFF**.
   - *Result:* Clearing sensor memory forces the LC-1 controller to perform a full heater calibration on the next power cycle.

---

### Phase 2: Free Air Sensor Calibration
1. Ensure the O2 sensor is reconnected to the LC-1 6-pin harness and **suspended in clean ambient air**.
2. Turn vehicle ignition **ON** (Engine OFF). Do NOT start the engine!
3. **Monitor Status LED Warm-up:**
   - The red LED (or calibration button LED) will flash steadily for **30–60 seconds** as the controller heats the sensor element to $750^\circ\text{C}$.
   - Once heated, the LED will illuminate **SOLID RED** for 2 seconds, then turn **OFF** for 2 seconds.
4. **Trigger Free Air Calibration:**
   - Press and hold the **Calibration Pushbutton** (or ground the black calibration wire) for **2 to 3 seconds**, then release.
   - *Behavior:* The status LED will flash rapidly for **15 to 30 seconds** while the LC-1 measures ambient oxygen content ($20.9\%\text{ O}_2$).
5. **Calibration Complete:**
   - The status LED will stop flashing and remain **SOLID RED**.
6. Turn vehicle ignition **OFF**.

---

### Phase 3: Reinstallation & Verification
1. Reinstall the O2 sensor into the exhaust bung / tailpipe sniffer.
2. Turn ignition **ON** and verify VCM Scanner channel `[MPVI2.1 -> Innovate - LC-1]`.
3. With engine OFF and exhaust clear, measured Lambda should read **$1.000\lambda$** (or $20.9\%\text{ O}_2$).

---

## 4. Analog Ground Offset Calibration in VCM Scanner

If the LC-1 wideband still displays a constant offset in VCM Scanner after Free Air Calibration, calibrate the MPVI analog ground offset:

### Ground Offset Adjustment Formula
$$\text{Calculated Lambda} = \left(\frac{V_{\text{measured}}}{5.0}\right) \times (\text{Lambda}_{\text{max}} - \text{Lambda}_{\text{min}}) + \text{Lambda}_{\text{min}} + \text{Offset}$$

### For Standard Innovate LC-1 0–5V Transfer Function ($0\text{V} = 0.500\lambda$, $5\text{V} = 1.523\lambda$):
$$\text{Lambda} = (V_{\text{MPVI}} \times 0.2046) + 0.500 + \text{Offset}$$

- **If Wideband reads 0.10 Lambda LEANer than actual:** Enter offset **`-0.100`** in VCM Scanner Math Parameter.
- **If Wideband reads 0.10 Lambda RICHER than actual:** Enter offset **`+0.100`** in VCM Scanner Math Parameter.

---

## 5. Summary Troubleshooting Matrix

| Symptom | Probable Cause | Action Required |
|---|---|---|
| LED Flashes 2 Times | Sensor disconnected or damaged harness | Check 6-pin connector wiring |
| LED Flashes 8 Times | Sensor element overheating ($>900^\circ\text{C}$) | Add copper heat-sink wash / move sensor downstream |
| Log shows $1.15\lambda$ while O2 is $0.85\text{V}$ | Ground voltage offset or tailpipe air ingress | Run Free Air Calibration & check ground offset math |
