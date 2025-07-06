#include <ESP32Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;

int servo1pin = 1;
int ledpin = 2;
int servo2pin = 45;
int servo3pin = 20;

int target1 = 0, target2 = 0, target3 = 0;
int pos1 = 0, pos2 = 0, pos3 = 0;

void setup() {
  Serial.begin(115200);

  servo1.attach(servo1pin);
  servo2.attach(servo2pin);
  servo3.attach(servo3pin);
  pinMode(ledpin, OUTPUT);

  // Posición inicial
  servo1.write(pos1);
  servo2.write(pos2);
  servo3.write(pos3);

  digitalWrite(ledpin, LOW);
}

void loop() {
  // Leer comandos serial
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("S")) {
      int a1, a2, a3;
      int matched = sscanf(input.c_str(), "S %d %d %d", &a1, &a2, &a3);
      if (matched == 3) {
        target1 = constrain(a1, 0, 180);
        target2 = constrain(a2, 0, 180);
        target3 = constrain(a3, 0, 180);
        Serial.printf("Moving to: %d %d %d\n", target1, target2, target3);
      } else {
        Serial.println("Format: S <a1> <a2> <a3>");
      }
    }
  }

  bool moving = false;

  pos1 = moveSmooth(pos1, target1, servo1, moving);
  pos2 = moveSmooth(pos2, target2, servo2, moving);
  pos3 = moveSmooth(pos3, target3, servo3, moving);

  digitalWrite(ledpin, moving ? HIGH : LOW);

  delay(10);
}

int moveSmooth(int current, int target, Servo& s, bool &movingFlag) {
  if (current == target) return current;

  movingFlag = true;
  int step = (target > current) ? 1 : -1;
  current += step;
  s.write(current);
  return current;
}
