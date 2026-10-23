# Lab Roadmap

Lab 0 is complete. Lab 1 has instructions, firmware and analysis tools ready, with measurements pending. Labs 2-5 are planned.

## Lab 1: Characterize the instrument

Status: [instructions and tools ready](../labs/lab1-characterize-instrument/README.md), data pending.

How accurate, noisy and fast is the INA219? Experiments: accuracy sweep (1-20 V), current linearity across 100 ohm to 10 kohm loads, noise from 1,000 samples, averaging versus speed, programmable gain ranges, ESP32 ADC nonlinearity versus INA219, and supply ripple visibility.

Starting point from Lab 0: single readings at 22 mA have a standard deviation of about 0.2 mA, while the 5-sample mean was within 0.2% of the reference.

## Lab 2: Component I-V characterization

LED forward voltage by color at 1, 5, 10 and 20 mA; diode forward curves and reverse leakage; resistor tolerance across 20 parts; thermistor and photoresistor over time; RC charge and discharge time constant; PN2222 current gain.

## Lab 3: Power profiling

ESP32 power by state (CPU frequency, Wi-Fi, BLE, light and deep sleep), DC motor inrush and stall, servo, stepper (full versus half step), relay pull-in and holding voltage, buzzers, LCD backlight. Derived: energy per event and battery-life estimates.

## Lab 4: The bench supply under stress

Load regulation, CV-to-CC knee, transient response, light-load behavior of a switching supply, MB102 module efficiency versus load and input voltage, and dropout voltage.

## Lab 5: Capstones

Programmable I-V curve tracer, Wi-Fi power logger with web dashboard, smart current limiter with relay trip-time measurement, battery discharge tester.
