# Lab 1: Characterize the Instrument

**Time:** one session, about 2 to 3 hours

**Goal:** find out how accurate, noisy and fast the INA219 is, so every later lab can state how far its numbers can be trusted. Lab 0 gave a first look: at 22 mA a 5-sample mean was within 0.2% of the reference, but single readings wandered by about 0.2 mA. This lab turns that observation into measured limits.

> **Status:** instructions, firmware and analysis scripts are ready. Measurements have not been taken yet. Results will be added to [RESULTS.md](RESULTS.md).

## New to electronics? Read this first

Think of electricity as water in pipes:

- **Voltage (volts, V)** is the water pressure.
- **Current (amps, A; here milliamps, mA)** is how much water flows per second.
- **Resistance (ohms, Ω)** is how narrow the pipe is.

They are linked by Ohm's law: **voltage = current × resistance**. Five volts across a 220 Ω resistor gives 5 / 220 = 22.7 mA.

The INA219 measures current indirectly. Inside it is a tiny 0.1 Ω resistor (the **shunt**). Current through it creates a very small voltage (22 mA × 0.1 Ω = 2.2 mV), and the chip measures that voltage and converts it back to current. Its smallest step is 10 µV across the shunt, which is **0.1 mA** of current.

Lab 1 is like putting a known weight on a bathroom scale before trusting it. You give the INA219 situations where you already know the answer and see how wrong it is, and in what way.

| Term | Plain meaning |
|---|---|
| Gain error | The instrument reads a fixed percentage too high or low everywhere |
| Offset error | The instrument reads something other than zero when the true value is zero |
| Noise | The reading wobbles even when the true value is steady |
| Standard deviation | The typical size of that wobble |
| Resolution | The smallest step the instrument can show |
| Count | One step of resolution (here 10 µV across the shunt) |

## What you will learn

- The INA219's gain and offset error against a multimeter reference
- The current level below which its readings stop being useful
- Noise per reading, and how averaging trades it against sample rate
- What the programmable gain setting does and does not improve
- How the ESP32's built-in ADC compares with the INA219 as a voltmeter
- Whether the supply's ripple is visible at all

## Write down predictions first

Before taking any data, record your guess for each item. Comparing predictions with results is the most useful part of the lab.

1. Current error at 22 mA will be below 1%.
2. Readings below about 1 mA will be unreliable.
3. Standard deviation will fall roughly as 1/√N with averaging.
4. A smaller gain range will give finer current resolution.
5. The ESP32 ADC will be less linear than the INA219 near both ends of its range.

Prediction 4 is worth thinking about. The datasheet describes the shunt-voltage step as 10 µV in every gain range, so the experiment may disprove it.

## Materials

- Everything from [Lab 0](../lab0-bring-up/README.md) (NodeMCU-32S, INA219, bench supply, breadboard, jumpers, multimeter)
- Resistors: 100 Ω, 220 Ω, 1 kΩ, 2.2 kΩ, 10 kΩ, 47 kΩ, and two 1 kΩ for the ADC divider. Measure each one with the multimeter, out of circuit, and write down the value.
- A notebook or spreadsheet for the data log

## Safety and setup rules

1. Follow the Lab 0 rules: current limit set before connecting, common ground, output off while rewiring, INA219 kept at or below about 24 V.
2. **Check resistor power before every run.** Power in a resistor is P = V² / R. A 1/4 W resistor is only safe up to 0.25 W, and you should stay under about 0.2 W so it does not get hot.

| Resistor | Maximum voltage (about 0.2 W) |
|---|---|
| 100 Ω | 4.4 V |
| 220 Ω | 6.6 V |
| 1 kΩ | 14 V |
| 2.2 kΩ | 21 V |
| 10 kΩ | above 26 V (limited by the INA219) |

3. Set the supply current limit just above what each run needs (for example 0.10 A for the low-voltage runs, 0.03 A for the high-voltage runs).
4. Never exceed 3.3 V on an ESP32 pin. The ADC experiment uses a divider to keep the pin at or below 3.0 V.

## INA219 register reference

The Lab 1 firmware reads the INA219 registers directly, so you control the settings that the Adafruit library hides.

| Register | Address | Contents |
|---|---|---|
| Configuration | 0x00 | Bus range, gain, ADC resolution and averaging, mode |
| Shunt voltage | 0x01 | Signed, 10 µV per count |
| Bus voltage | 0x02 | Bits 15 to 3 are the value (4 mV per count). Bit 1 is CNVR (new data ready). Bit 0 is OVF (overflow). |
| Power | 0x03 | Reading it clears CNVR (used here to detect fresh samples) |

**Configuration bits:** bit 13 selects the 32 V bus range, bits 12 and 11 select the gain, bits 10 to 7 set the bus ADC mode, bits 6 to 3 set the shunt ADC mode, and bits 2 to 0 set the operating mode (7 means continuous shunt and bus).

**Gain codes**

| Code | Shunt range | Maximum current with a 0.1 Ω shunt |
|---|---|---|
| 0 | ±40 mV | 400 mA |
| 1 | ±80 mV | 800 mA |
| 2 | ±160 mV | 1.6 A |
| 3 | ±320 mV | 3.2 A |

**ADC mode codes** (both ADCs use the same code)

| Code | Resolution and averaging | Conversion time per ADC |
|---|---|---|
| 0x0 | 9-bit | 84 µs |
| 0x1 | 10-bit | 148 µs |
| 0x2 | 11-bit | 276 µs |
| 0x3 | 12-bit | 532 µs |
| 0x9 | 12-bit, 2 samples averaged | 1.06 ms |
| 0xA | 12-bit, 4 samples | 2.13 ms |
| 0xB | 12-bit, 8 samples | 4.26 ms |
| 0xC | 12-bit, 16 samples | 8.51 ms |
| 0xD | 12-bit, 32 samples | 17.02 ms |
| 0xE | 12-bit, 64 samples | 34.05 ms |
| 0xF | 12-bit, 128 samples | 68.10 ms |

The bus and shunt ADCs convert one after the other, so one full reading takes the sum of both. The effective rate is also limited by the time to read the registers over I2C.

## Firmware

Open [`firmware/ina219_characterize/ina219_characterize.ino`](firmware/ina219_characterize/ina219_characterize.ino) and upload it with the same board settings as Lab 0.

Open the Serial Monitor at 115200 baud with the line ending set to **Newline**. The first line should report a configuration register of `0x399F`. Commands:

| Command | Action |
|---|---|
| `g0` to `g3` | Set the gain code |
| `aX` | Set the ADC mode code in hex (for example `aB`) |
| `nN` | Set samples per capture (for example `n200`) |
| `r` | Run one capture |
| `s` | Sweep all 11 averaging modes at the current gain |

Output is CSV: `label,i,t_us,bus_V,shunt_mV,current_mA,ovf`. Copy the Serial Monitor output into a file under `data/` for each experiment.

## Experiment 1: Accuracy sweep

**Question:** what are the INA219's gain and offset errors for voltage and current?

There are two runs, because one resistor cannot cover the full voltage range safely.

**Run A: low voltage, 220 Ω** (current limit 0.10 A)

1. Wire the Lab 0 circuit with the 220 Ω resistor. Send `g3`, `aB`, `n50`.
2. Set the supply to 1, 2, 3, 4, 5 and 6 V in turn. At each step read the supply display, measure the voltage across the resistor with the multimeter, then send `r` and save the 50 samples.
3. Keep every run under 0.2 W (6 V maximum on 220 Ω).

**Run B: high voltage, 2.2 kΩ** (current limit 0.03 A)

1. Swap in the 2.2 kΩ resistor.
2. Repeat at 6, 8, 10, 12, 15 and 20 V. Never go above 20 V on the INA219 for this experiment.

**Record per step:** supply display, multimeter voltage at the INA219 Vin- terminal (to rail), multimeter voltage across the resistor, mean INA219 bus voltage, mean INA219 current, and the reference current (resistor voltage ÷ measured resistance).

**Analysis:** put the (reference, measured) pairs in a two-column CSV and run:

```
python analysis/fit_accuracy.py data/current_accuracy.csv
```

The slope is the gain error (1.0 means none) and the intercept is the offset. Do the same for voltage.

**What to expect:** current error under 1% at several mA to tens of mA (Lab 0 saw +0.2% at 22 mA). The open Lab 0 question of a 63 mV difference between the INA219 bus reading and the voltage across the resistor will show up here as a voltage offset that either stays constant (a contact drop in the wiring) or grows with current.

## Experiment 2: Current linearity and the low-current floor

**Question:** at what current does the INA219 stop being useful?

The fixed voltage is 3.0 V, which keeps every resistor under 0.1 W.

1. Set the supply to 3.0 V with a 0.05 A limit. Send `g3`, `aB`, `n100`.
2. For each resistor (100 Ω, 220 Ω, 1 kΩ, 2.2 kΩ, 10 kΩ, 47 kΩ), measure its resistance out of circuit, wire it as the load, and capture.
3. Compute the expected current as the multimeter voltage across the resistor ÷ measured resistance.

| Resistor | Expected current at 3.0 V | Shunt voltage | Counts of 10 µV |
|---|---|---|---|
| 100 Ω | about 30 mA | about 3.0 mV | about 300 |
| 220 Ω | about 13.6 mA | about 1.4 mV | about 140 |
| 1 kΩ | about 3.0 mA | about 0.30 mV | about 30 |
| 2.2 kΩ | about 1.4 mA | about 0.14 mV | about 14 |
| 10 kΩ | about 0.30 mA | about 0.03 mV | about 3 |
| 47 kΩ | about 0.064 mA | about 0.006 mV | less than 1 |

**Analysis:** plot measured against expected current on log-log axes, and percent error against current. Find the current where the error exceeds 5% and where the reading is no longer distinguishable from the zero offset.

**What to expect:** with a 0.1 Ω shunt the step is 0.1 mA, so error becomes large below a few mA (0.1 mA is 3% of 3 mA) and the 47 kΩ case is below one count. This is why Lab 3 cannot resolve ESP32 deep sleep with this breakout.

## Experiment 3: Noise

**Question:** how noisy is a single reading?

1. Use the 220 Ω load at 5 V (the Lab 0 circuit, 0.10 A limit).
2. Send `g3`, `a3`, `n1000`, then `r`. This is 12-bit with no averaging. Save the 1,000 samples.
3. Repeat with the load removed (Vin+ and Vin- unconnected) to measure the zero offset and its noise.

**Analysis:** run `python analysis/analyze_lab1.py data/noise.csv` for mean, standard deviation and range. Plot a histogram of the current values and a time series. Express noise in counts (standard deviation ÷ 10 µV) as well as in mA.

**What to expect:** Lab 0 showed a standard deviation of about 0.2 mA, which is two counts. Look for steps in the histogram at multiples of 0.1 mA, because the data is quantized.

## Experiment 4: Averaging versus speed

**Question:** how much does averaging reduce noise, and what does it cost in sample rate?

1. Keep the 220 Ω load at 5 V and gain code 3.
2. Send `n300` then `s`. The sketch captures 300 samples at each of the 11 ADC modes (9-bit up to 12-bit with 128 averages). Save everything in one file.
3. Run `python analysis/analyze_lab1.py data/averaging_sweep.csv`.

**Analysis:** the script prints one row per mode with the sample rate and the standard deviation. Add a column for the standard deviation you would expect if noise fell as 1/√N, and plot noise against sample rate on log-log axes.

**What to expect:** noise should fall as you average more, with the sample rate dropping from the kilohertz range to about 7 per second at 128 averages. At the fast end the rate is limited by I2C and the polling loop, not just conversion time. Averaging helps random noise but not a fixed offset.

## Experiment 5: Gain range

**Question:** does a smaller range improve resolution?

1. Use a small current, for example 220 Ω at 3 V (about 13.6 mA, 1.4 mV across the shunt), at ADC code `B`.
2. For each gain code (`g0`, `g1`, `g2`, `g3`), send `n200` and `r`.
3. Compare mean and standard deviation across the four gains.
4. **Clipping test (optional):** the other loads in this lab put only a few mV across the shunt, so they will not clip. To force clipping, use a 10 Ω, 5 W resistor at 5 V (about 500 mA and 2.5 W, so it gets hot; keep each run brief) with the supply current limit set to 0.6 A first. At gain code 0 (±40 mV) the 50 mV shunt voltage exceeds the range and the reading should stop near 40 mV. The other gain codes should read about 50 mV. Skip this test if you do not have the resistor.

**Analysis:** compare the shunt-voltage standard deviation in counts across gains.

**What to expect:** based on the datasheet, the 10 µV step is the same in all ranges, so resolution should not improve. A smaller range only lowers the maximum current. Libraries that report finer current steps in the smaller ranges are re-scaling the same data, not measuring more finely. If your result disagrees, record it and investigate.

## Experiment 6: ESP32 ADC versus INA219

**Question:** how linear is the ESP32's built-in ADC compared with the INA219 as a voltmeter?

**Wiring** (supply off)

```
Supply (+) -> INA219 Vin+ -> Vin- -> 1 kΩ -> midpoint -> 1 kΩ -> ground rail
Midpoint -> ESP32 GPIO34 (ADC1, input only)
```

The midpoint is half the bus voltage. Two equal 1 kΩ resistors keep the source impedance low (about 500 Ω) and the load current at 0.5 mA per volt, which the INA219 can resolve.

1. Keep the supply at or below 6.0 V so the midpoint never exceeds 3.0 V. Check with the multimeter before connecting GPIO34.
2. Upload [`firmware/adc_vs_ina219/adc_vs_ina219.ino`](firmware/adc_vs_ina219/adc_vs_ina219.ino). It averages 64 ADC readings per line on GPIO34 (ADC1, 11 dB attenuation) and prints `adc_mV,ina_bus_V,ina_mid_mV`.
3. Step the supply from 0.5 V to 6.0 V in 0.5 V increments. At each step, record the multimeter voltage at the midpoint beside one printed line.

**Analysis:** plot the ADC reading and the INA219 midpoint reading each against the multimeter reference, and plot each one's error in mV across the range. `analysis/fit_accuracy.py` gives the slope and offset for each.

**What to expect:** the ESP32 ADC is known to be nonlinear near the bottom and top of its range. The INA219 (4 mV steps) should track the meter more closely. Both results are measurements, so report what you find.

## Experiment 7: Supply ripple visibility

**Question:** can the INA219 see the bench supply's switching noise?

1. Use the 220 Ω load at 5 V and ADC code `0` (9-bit, fastest).
2. Capture 1,000 samples and plot current and bus voltage against time.
3. Compare the noise with the 12-bit, 128-average capture from Experiment 4.

**Expect and report honestly:** switching supplies typically ripple at tens of kilohertz or higher, far faster than this setup can sample. The INA219 will not display the actual ripple. At best, ripple adds to the apparent noise or aliases into slow variations. This is a limit of the instrument and worth recording. Seeing true ripple needs an oscilloscope.

## Analysis summary

1. **Gain and offset:** slope and intercept from the Experiment 1 fits, for voltage and for current.
2. **Noise:** standard deviation in mA and in counts for single 12-bit readings.
3. **Effective resolution:** the span of the range divided by about 6.6 times the standard deviation gives a noise-free number of counts. Convert to bits with log₂.
4. **Floor:** the lowest current with under 5% error.
5. **Best settings:** the ADC mode and gain you recommend for later labs, with reasoning.

## Deliverables

1. Predictions written before the experiments
2. Accuracy plots with fit equations (Experiment 1)
3. Linearity plot and the low-current floor (Experiment 2)
4. Noise histogram and zero-offset statistics (Experiment 3)
5. Noise versus sample rate table and plot (Experiment 4)
6. Gain comparison table with a short conclusion (Experiment 5)
7. ESP32 ADC versus INA219 error plot (Experiment 6)
8. A paragraph on ripple visibility (Experiment 7)
9. Recommended INA219 settings for Labs 2 to 5, and the measured limits of the instrument
10. Raw CSV files for every experiment, saved under `data/`

Fill in [RESULTS.md](RESULTS.md) as you go.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Config register does not read 0x399F at startup | The INA219 is not responding, or a prior sketch changed it. Power-cycle the board and recheck the I2C wiring. |
| `timeout` printed during a capture | No new conversions. Check the INA219 is powered and the commands were accepted. |
| `ovf` column shows 1 | Overflow. Check the voltage is within range and the gain code matches the current. |
| Current shows a fixed offset at zero load | The expected zero offset. Record it in Experiment 3 and subtract it in later labs. |
| Readings drift slowly | Resistors heating up, or the supply settling. Wait 30 seconds after each change and keep resistor power under 0.2 W. |
| ESP32 ADC reads 0 or saturates | Wrong pin (use GPIO34, ADC1) or the midpoint is above the attenuation range. Keep the pin at or below 3.0 V. |
| Garbled serial output | Baud rate must be 115200. Press EN to reset the board. |
