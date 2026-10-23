// Lab 0, Steps 5 and 7: INA219 reader for the ESP32 (NodeMCU-32S).
//
// Requires the "Adafruit INA219" library (and its Adafruit BusIO dependency).
// Wiring: INA219 VCC->3V3, GND->GND, SDA->GPIO21, SCL->GPIO22.
#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina;

const int SDA_PIN = 21;
const int SCL_PIN = 22;
const unsigned long SAMPLE_MS = 1000;

// true  = labeled, human-readable lines (for watching the Serial Monitor)
// false = plain CSV (for logging and plotting)
const bool READABLE = true;

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);

  if (!ina.begin()) {
    Serial.println("INA219 not found. Check SDA/SCL/VCC/GND wiring.");
    while (true) delay(10);
  }

  if (READABLE) {
    Serial.println("INA219 connected at 0x40");
    Serial.println("-----------------------------------------------");
    Serial.println("Bus     = voltage at the Vin- terminal (V)");
    Serial.println("Shunt   = voltage across the 0.1 ohm shunt (mV)");
    Serial.println("Load    = Bus + Shunt = voltage at Vin+ (V)");
    Serial.println("Current = current through the shunt (mA)");
    Serial.println("Power   = Bus x Current (mW)");
    Serial.println("-----------------------------------------------");
  } else {
    Serial.println("ms,bus_V,shunt_mV,current_mA,power_mW");
  }
}

void loop() {
  float bus_V      = ina.getBusVoltage_V();
  float shunt_mV   = ina.getShuntVoltage_mV();
  float current_mA = ina.getCurrent_mA();
  float power_mW   = ina.getPower_mW();
  float load_V     = bus_V + (shunt_mV / 1000.0);

  if (READABLE) {
    Serial.printf("t=%6.1f s | Bus: %6.3f V | Shunt: %7.3f mV | Load: %6.3f V | Current: %8.2f mA | Power: %8.2f mW\n",
                  millis() / 1000.0, bus_V, shunt_mV, load_V, current_mA, power_mW);
  } else {
    Serial.printf("%lu,%.3f,%.3f,%.2f,%.2f\n",
                  millis(), bus_V, shunt_mV, current_mA, power_mW);
  }
  delay(SAMPLE_MS);
}
