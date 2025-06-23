#include <Arduino.h>
#include "Seeed_Arduino_mmWave.h"

// Set up serial communication depending on the board type
#ifdef ESP32
#  include <HardwareSerial.h>
HardwareSerial mmWaveSerial(0);
#else
#  define mmWaveSerial Serial1
#endif

//Board: XIAO_ESP32C6

SEEED_MR60BHA2 mmWave;

void setup() {
  Serial.begin(115200);
  mmWave.begin(&mmWaveSerial);
}

float breath_rate, heart_rate;

void loop() {
  if (mmWave.update(1000)) {
  
  // if (mmWave.getHeartBreathPhases(total_phase, breath_phase, heart_phase)) {
  //   Serial.printf("total_phase: %.2f\t", total_phase);
  //   Serial.printf("breath_phase: %.2f\t", breath_phase);
  //   Serial.printf("heart_phase: %.2f\n", heart_phase);
  // }

  // if (mmWave.getBreathRate(breath_rate)) {
  //   Serial.printf("breath_rate: %.2f\n", breath_rate);
  // }

  // if (mmWave.getHeartRate(heart_rate)) {
  //   Serial.printf("heart_rate: %.2f\n", heart_rate);
  // }

  // if (mmWave.getDistance(distance)) {
  //   Serial.printf("distance: %.2f\n", distance);
  // }
    // mmWave.getHeartBreathPhases(total_phase, breath_phase, heart_phase);
    mmWave.getBreathRate(breath_rate);
    mmWave.getHeartRate(heart_rate);
    // mmWave.getDistance(distance);

    float check = breath_rate + heart_rate;

    if (check>0.0)
    {
      Serial.printf("%.2f,%.2f", breath_rate, heart_rate);
      Serial.println("");
    }  
  
  }
}