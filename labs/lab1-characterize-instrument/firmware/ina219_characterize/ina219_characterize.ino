// Lab 1: INA219 characterization logger for the ESP32 (NodeMCU-32S).
//
// Talks to the INA219 registers directly so gain and averaging can be changed.
// Current is computed from the shunt voltage (I = V / R), so no calibration
// register is needed.
//
// Serial commands (115200 baud, line ending = Newline):
//   g0..g3   gain code: 0 = +/-40 mV, 1 = +/-80, 2 = +/-160, 3 = +/-320 mV
//   aX       ADC mode code in hex (see the Lab 1 README table)
//   nN       samples per capture
//   r        run one capture
//   s        sweep all averaging modes at the current gain
//
// Output: label,i,t_us,bus_V,shunt_mV,current_mA,ovf
#include <Wire.h>

const uint8_t INA_ADDR = 0x40;
const int SDA_PIN = 21;
const int SCL_PIN = 22;
const float R_SHUNT_OHMS = 0.1;      // use your measured shunt value if you have one

const uint8_t REG_CONFIG = 0x00;
const uint8_t REG_SHUNT  = 0x01;
const uint8_t REG_BUS    = 0x02;
const uint8_t REG_POWER  = 0x03;

uint8_t  pg = 3;          // gain code 0..3
uint8_t  adcCode = 0x3;   // ADC mode code (12-bit, no averaging)
uint16_t samples = 200;

void writeReg(uint8_t reg, uint16_t val) {
  Wire.beginTransmission(INA_ADDR);
  Wire.write(reg);
  Wire.write(val >> 8);
  Wire.write(val & 0xFF);
  Wire.endTransmission();
}

uint16_t readReg(uint8_t reg) {
  Wire.beginTransmission(INA_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(INA_ADDR, (uint8_t)2);
  uint16_t v = (uint16_t)Wire.read() << 8;
  v |= Wire.read();
  return v;
}

void applyConfig() {
  uint16_t cfg = (1 << 13) | (pg << 11) | (adcCode << 7) | (adcCode << 3) | 0x7;
  writeReg(REG_CONFIG, cfg);
}

bool waitForConversion(uint32_t timeout_ms) {
  uint32_t t0 = millis();
  while (millis() - t0 < timeout_ms) {
    if (readReg(REG_BUS) & 0x0002) return true;   // CNVR set
    delayMicroseconds(50);
  }
  return false;
}

void capture() {
  char label[24];
  snprintf(label, sizeof(label), "pg%u_adc%X", pg, adcCode);
  applyConfig();
  readReg(REG_POWER);               // clear CNVR
  waitForConversion(500);           // discard the first conversion
  readReg(REG_POWER);
  for (uint16_t i = 0; i < samples; i++) {
    if (!waitForConversion(500)) { Serial.println("timeout"); return; }
    uint32_t t_us = micros();
    int16_t  shunt = (int16_t)readReg(REG_SHUNT);
    uint16_t bus   = readReg(REG_BUS);
    readReg(REG_POWER);             // clear CNVR for the next sample
    float shunt_mV   = shunt * 0.01;
    float bus_V      = (bus >> 3) * 0.004;
    float current_mA = shunt_mV / R_SHUNT_OHMS;
    Serial.printf("%s,%u,%lu,%.3f,%.2f,%.2f,%u\n", label, i, t_us,
                  bus_V, shunt_mV, current_mA, bus & 1);
  }
}

void sweepAveraging() {
  const uint8_t codes[] = {0x0, 0x1, 0x2, 0x3, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF};
  for (uint8_t c : codes) { adcCode = c; capture(); }
}

void handle(String s) {
  s.trim();
  if (s.length() == 0) return;
  const char* arg = s.c_str() + 1;
  switch (s[0]) {
    case 'g': pg = constrain(atoi(arg), 0, 3); break;
    case 'a': adcCode = strtol(arg, nullptr, 16) & 0xF; break;
    case 'n': samples = max(1, atoi(arg)); break;
    case 'r': capture(); return;
    case 's': sweepAveraging(); return;
    default: break;
  }
  Serial.printf("# gain=%u adc=0x%X samples=%u\n", pg, adcCode, samples);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);
  Serial.printf("# config register at reset: 0x%04X (expect 0x399F)\n", readReg(REG_CONFIG));
  Serial.println("# commands: g0-3 gain | aX adc mode (hex) | nN samples | r run | s sweep averaging");
  Serial.println("label,i,t_us,bus_V,shunt_mV,current_mA,ovf");
}

void loop() {
  if (Serial.available()) handle(Serial.readStringUntil('\n'));
}
