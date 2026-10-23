# Lab 1 Results

**Status:** not yet measured. This file is the template; fill it in as each experiment is completed.

**Date:**
**Settings used (gain code, ADC code, supply current limit):**

## Predictions (written before measuring)

| # | Prediction | Result | Right or wrong? |
|---|---|---|---|
| 1 | Current error at 22 mA below 1% | | |
| 2 | Readings below about 1 mA unreliable | | |
| 3 | Noise falls as 1/sqrt(N) with averaging | | |
| 4 | Smaller gain range gives finer resolution | | |
| 5 | ESP32 ADC less linear than INA219 near the ends | | |

## Experiment 1: Accuracy

| Quantity | Slope (gain) | Intercept (offset) | Max error vs reference |
|---|---|---|---|
| Current (mA) | | | |
| Bus voltage (V) | | | |

Notes on the Lab 0 voltage gap (INA219 bus versus voltage across the resistor):

## Experiment 2: Low-current floor

| Resistor (measured) | Expected mA | INA219 mean mA | Error % |
|---|---|---|---|
| 100 ohm | | | |
| 220 ohm | | | |
| 1 kohm | | | |
| 2.2 kohm | | | |
| 10 kohm | | | |
| 47 kohm | | | |

Lowest current with error under 5%:

## Experiment 3: Noise (12-bit, no averaging)

| Condition | Mean mA | Std dev mA | Std dev in counts | Range mA |
|---|---|---|---|---|
| 220 ohm at 5 V | | | | |
| No load (zero offset) | | | | |

## Experiment 4: Averaging versus speed

| ADC code | Mode | Rate (Hz) | Std dev (mA) | Expected 1/sqrt(N) |
|---|---|---|---|---|
| 0x0 | 9-bit | | | |
| 0x3 | 12-bit | | | |
| 0xB | 12-bit, 8 avg | | | |
| 0xF | 12-bit, 128 avg | | | |

## Experiment 5: Gain range

| Gain code | Range | Mean mA | Std dev (counts) |
|---|---|---|---|
| 0 | +/-40 mV | | |
| 1 | +/-80 mV | | |
| 2 | +/-160 mV | | |
| 3 | +/-320 mV | | |

Conclusion on resolution versus range:

## Experiment 6: ESP32 ADC versus INA219

| Multimeter mV (midpoint) | ESP32 ADC mV | ADC error mV | INA219 mid mV | INA219 error mV |
|---|---|---|---|---|
| | | | | |

## Experiment 7: Ripple

Observed:

## Recommended settings for Labs 2 to 5

- Gain code:
- ADC mode:
- Samples to average:
- Stated limits of the instrument:
