#include <ESP32Servo.h>

#define STOP 95

Servo s1, s2, s3;
const int pin1 = 23;
const int pin2 = 19;
const int pin3 = 18;

float v1, v2, v3;

void setup() {
  Serial.begin(115200);
  s1.attach(pin1);
  s2.attach(pin2);
  s3.attach(pin3);
  stopAll();
  Serial.println("🌀 Velocity-only servo firmware ready. Use: V pwm1 pwm2 pwm3");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.startsWith("V ")) {
      if (sscanf(cmd.c_str(), "V %f %f %f", &v1, &v2, &v3) == 3) {
        int p1 = constrain((int)v1, 0, 180);
        int p2 = constrain((int)v2, 0, 180);
        int p3 = constrain((int)v3, 0, 180);
        s1.write(p1);
        s2.write(p2);
        s3.write(p3);
        Serial.printf("✅ Set PWM: %d, %d, %d\n", p1, p2, p3);
      } else {
        Serial.println("❌ Invalid V format. Use: V pwm1 pwm2 pwm3");
      }
    }
  }
}

void stopAll() {
  s1.write(STOP);
  s2.write(STOP);
  s3.write(STOP);
}