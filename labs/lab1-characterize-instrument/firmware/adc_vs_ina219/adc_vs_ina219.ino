// Lab 1, Experiment 6: ESP32 built-in ADC versus INA219 bus voltage.
//
// Wiring (supply off):
//   Supply (+) -> INA219 Vin+ -> Vin- -> 1k -> midpoint -> 1k -> ground rail
//   Midpoint -> GPIO34 (ADC1, input only)
// Keep the supply at or below 6.0 V so the midpoint never exceeds 3.0 V.
//
// Each line is one averaged point. Type the multimeter reading of the midpoint
// into your notes next to each line.
//
// Output: adc_mV,ina_bus_V,ina_mid_mV
#include <Wire.h>

const uint8_t INA_ADDR = 0x40;
const int SDA_PIN = 21;
const int SCL_PIN = 22;
const int ADC_PIN = 34;
const int AVG_COUNT = 64;

uint16_t readReg(uint8_t reg) {
  Wire.beginTransmission(INA_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(INA_ADDR, (uint8_t)2);
  uint16_t v = (uint16_t)Wire.read() << 8;
  v |= Wire.read();
  return v;
}

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  analogSetPinAttenuation(ADC_PIN, ADC_11db);
  Serial.println("adc_mV,ina_bus_V,ina_mid_mV");
}

void loop() {
  uint32_t sum = 0;
  for (int i = 0; i < AVG_COUNT; i++) {
    sum += analogReadMilliVolts(ADC_PIN);
    delay(2);
  }
  float adc_mV = sum / (float)AVG_COUNT;
  float bus_V = (readReg(0x02) >> 3) * 0.004;   // INA219 default config is fine here
  Serial.printf("%.1f,%.3f,%.1f\n", adc_mV, bus_V, bus_V * 500.0);
  delay(1000);
}
