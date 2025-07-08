#include <ESP32Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;

const int ledpin = 2;

const int servo1pin = 1;
const int servo2pin = 45;
const int servo3pin = 20;

int pos1 = 90, pos2 = 90, pos3 = 90;
int target1 = 0, target2 = 0, target3 = 0;

// Velocidad máxima de movimiento (grados por segundo)
const int speedDegPerSec = 90;
int stepSize = 2;  // Se puede modificar vía serial

void setup() {
  Serial.begin(115200);

  servo1.attach(servo1pin);
  servo2.attach(servo2pin);
  servo3.attach(servo3pin);
  pinMode(ledpin, OUTPUT);

  servo1.write(pos1);
  servo2.write(pos2);
  servo3.write(pos3);

  digitalWrite(ledpin, LOW);
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("S")) {
      int a1, a2, a3, sSize;
      int matched = sscanf(input.c_str(), "S %d %d %d %d", &a1, &a2, &a3, &sSize);
      if (matched >= 3) {
        a1 = constrain(a1, 0, 180);
        a2 = constrain(a2, 0, 180);
        a3 = constrain(a3, 0, 180);
        if (matched == 4) {
          stepSize = constrain(sSize, 1, 20); // límites razonables
        }

        target1 = a1;
        target2 = a2;
        target3 = a3;
        Serial.printf("Smooth move to: %d %d %d (step size %d)\n", target1, target2, target3, stepSize);
      } else {
        Serial.println("Format: S <a1> <a2> <a3> [stepSize]");
      }
    } else if (input.startsWith("D")) {
      int a1, a2, a3;
      int matched = sscanf(input.c_str(), "D %d %d %d", &a1, &a2, &a3);
      if (matched == 3) {
        a1 = constrain(a1, 0, 180);
        a2 = constrain(a2, 0, 180);
        a3 = constrain(a3, 0, 180);

        pos1 = target1 = a1;
        pos2 = target2 = a2;
        pos3 = target3 = a3;

        servo1.write(pos1);
        servo2.write(pos2);
        servo3.write(pos3);

        Serial.printf("Direct move to: %d %d %d\n", pos1, pos2, pos3);
      } else {
        Serial.println("Format: D <a1> <a2> <a3>");
      }
    }
  }

  static unsigned long lastStep = 0;
  unsigned long now = millis();
  float stepDelayMs = 1000.0 / speedDegPerSec;

  if (now - lastStep >= stepDelayMs) {
    lastStep = now;
    bool moving = false;

    pos1 = moveSmooth(pos1, target1, servo1, moving);
    pos2 = moveSmooth(pos2, target2, servo2, moving);
    pos3 = moveSmooth(pos3, target3, servo3, moving);

    digitalWrite(ledpin, moving ? HIGH : LOW);
  }
}

int moveSmooth(int current, int target, Servo& s, bool &movingFlag) {
  if (current == target) return current;

  movingFlag = true;
  int step = (target > current) ? stepSize : -stepSize;
  if (abs(target - current) < abs(step)) {
    current = target;
  } else {
    current += step;
  }
  s.write(current);
  return current;
}
