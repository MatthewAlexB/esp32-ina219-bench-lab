# Lab 0: Bring-Up

**Time:** about 30 minutes

**Objective:** confirm the ESP32 can talk to the INA219 over I2C, measure the INA219's zero offset, and do a first sanity check of its readings against the supply display and a multimeter.

## Materials

- NodeMCU-32S (ESP32-S), powered by USB from your computer
- INA219 breakout board
- Bench supply with test leads (written for a Jesverity SPS-3010)
- 220 ohm resistor (1/4 W)
- Breadboard and male-to-male jumper wires
- Multimeter (optional but strongly recommended; see Step 7)

## Safety

1. **Set the current limit before connecting anything.** The supply can deliver far more current than the INA219 can survive. Use 0.10 A.
2. Stay at or below about **24 V** on anything connected to the INA219 (its limit is 26 V). This lab uses 5 V.
3. Never apply more than **3.3 V** to ESP32 GPIO pins.
4. Turn the supply output **off** before every wiring change.
5. Power the ESP32 from **one source at a time**. In this lab it runs from USB only, so leave the VIN pin unconnected.

## Step 1: Install software and select the board

1. Install the Arduino IDE.
2. Add the ESP32 board package. In **File > Preferences**, add this URL to "Additional boards manager URLs":
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
3. In **Tools > Board > Boards Manager**, install **esp32 by Espressif Systems** (not the ESP8266 package).
4. Select **NodeMCU-32S** under **Tools > Board > esp32** (or **ESP32 Dev Module** if it is not listed).
5. Plug in the board and choose its COM port under **Tools > Port**. If no port appears, install the CP2102 or CH340 USB driver and try a data-capable cable.
6. In **Sketch > Include Library > Manage Libraries**, install **Adafruit INA219** and accept the Adafruit BusIO dependency.
7. If uploads fail, set **Upload Speed** to 115200 and hold the **BOOT** button while the IDE shows "Connecting......".

> **Compile error mentioning `hardware\avr`?** The IDE is still set to an Arduino Uno-style board. Re-select the ESP32 board. Typical symptoms are `no matching function for call to 'TwoWire::begin(int, int)'` and `HardwareSerial has no member named 'printf'`.

## Step 2: Set up the supply (nothing connected yet)

1. Plug in the supply with the output **disabled** and the test leads **not** connected to anything.
2. Set the voltage to **5.0 V** (coarse knob, then fine knob).
3. Set the current limit to **0.10 A**. The procedure depends on the model; check your manual. Verify it: with the voltage turned down, briefly short the leads and confirm the supply enters CC mode at about 0.10 A.
4. Identify the red (+) and black (-) terminals. **Leave the chassis earth terminal unconnected.** It is a mains safety ground, not the circuit's negative output.
5. Leave the output disabled until Step 7.

## Step 3: Wire the I2C connection (supply output still off)

| INA219 pin | NodeMCU-32S pin |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SDA | IO21 |
| SCL | IO22 |

Leave Vin+ and Vin- unconnected for now. The screw terminals on the INA219 are the **measurement path**, not the logic power.

## Step 4: Run the I2C scanner

Upload [`firmware/i2c_scan/i2c_scan.ino`](firmware/i2c_scan/i2c_scan.ino) and open the Serial Monitor at **115200 baud**.

**Expected:** `Found device at 0x40`.

**If nothing is found:** check that SDA and SCL are not swapped, check VCC and GND, check the solder joints on the header pins, and confirm the board is an INA219 and not a similar part. If the text is garbled, press the EN (reset) button once.

## Step 5: Measure the zero offset

1. Upload [`firmware/ina219_logger/ina219_logger.ino`](firmware/ina219_logger/ina219_logger.ino).
2. With Vin+ and Vin- **unconnected**, record about 30 seconds of output.
3. Compute the average shunt voltage and current. These are your **zero offset** values. Expect values near 0.00 mV and 0.0 mA, possibly within +/-0.1 mA.

Output is labeled by default:

```
t= 443.4 s | Bus:  4.988 V | Shunt:   2.260 mV | Load:  4.990 V | Current:    22.60 mA | Power:   114.00 mW
```

| Field | Meaning |
|---|---|
| Bus | Voltage at the Vin- terminal (V) |
| Shunt | Voltage across the on-board 0.1 ohm shunt (mV) |
| Load | Bus + Shunt, the voltage at Vin+ (V) |
| Current | Shunt voltage divided by the shunt resistance (mA) |
| Power | Bus x Current (mW) |

Set `READABLE = false` in the sketch to get plain CSV (`ms,bus_V,shunt_mV,current_mA,power_mW`) for plotting.

To save a capture, copy the Serial Monitor output into a file under `data/`, then run:

```
python analysis/analyze_log.py data/offset.log
```

## Step 6: Wire the load with a common ground

The supply has no dedicated common-ground wire, and none is needed. Common ground means the supply's black (-) terminal, the INA219 GND, and the ESP32 GND all connect to the same node. Use the breadboard's blue (-) rail.

![Lab 0 wiring diagram](images/wiring.svg)

With the supply output **off**:

1. Clip or plug the supply's black lead into the breadboard - rail.
2. Jumper the ESP32 GND and the INA219 GND to that rail.
3. Connect the far end of the 220 ohm resistor to the - rail.
4. Connect the supply's red lead to the INA219 **Vin+**, and a jumper from **Vin-** to the resistor.

Current must flow *through* the INA219 (in at Vin+, out at Vin-). If the resistor is wired directly across the supply, the INA219 reads zero. If current reads negative, Vin+ and Vin- are swapped.

Do not connect the supply's + terminal or the ESP32's 3.3 V pin to the - rail, and do not use the supply's USB port to power the ESP32 in this lab.

## Step 7: Compare readings

1. Confirm the current limit is still 0.10 A, then enable the supply output.
2. Record values from each source:

| Source | Voltage | Current |
|---|---|---|
| Supply display | | |
| INA219 (Bus or Load, current_mA) | | |
| Multimeter (across the resistor; in series for current if possible) | | |

3. **Expected:** about 5.0 V and about 22.7 mA (5 V / 220 ohm). Real resistors are +/-5% or +/-1%, so measure the actual resistance with the supply off and the resistor out of circuit, then compute the expected current from that.
4. Many 10 A supplies show current to only 0.01 A, which would read this load as roughly 0.02 A. Check your manual. If the display is that coarse, treat it as a rough check and use the multimeter as the current reference.
5. A switching supply can show more ripple than a linear one, so slightly jittery INA219 readings may be a real finding rather than a wiring fault.
6. Log about 30 seconds, then turn the output off. To compare against a reference:

```
python analysis/analyze_log.py data/load.log --ohms 221 --ref-volts 4.99
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Compile errors mentioning `avr` paths | Wrong board selected; choose NodeMCU-32S or ESP32 Dev Module |
| Upload stuck at "Connecting......" | Hold the BOOT button; check the USB cable and driver |
| Scanner finds nothing | SDA/SCL swapped, no 3.3 V or GND on the INA219, or a bad solder joint |
| Current reads 0 | Load wired around the INA219 |
| Negative current | Vin+ and Vin- swapped |
| Bus voltage reads 0 or is erratic | Missing common ground |
| Large or erratic current at idle | Floating Vin- picking up noise; connect the load first |
| Supply drops into CC mode | A short somewhere; turn off and recheck the wiring |

## Deliverables

1. Photo of the wiring
2. Scanner output showing 0x40
3. Zero-offset values: shunt mV and current mA, with mean and range
4. The Step 7 comparison table, with percent error for each source
5. Supply notes: display resolution for voltage and current, and whether the supply entered CC mode at your 0.10 A setting
6. One line: which instrument do you trust most, and why?

A fill-in template is in [RESULTS.md](RESULTS.md).
