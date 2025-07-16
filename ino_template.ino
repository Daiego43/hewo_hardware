#include <ESP32Servo.h>
#include <WiFi.h>
#include <WebServer.h>

// ---------- WiFi Config ----------
const char* ap_ssid = "{{AP_SSID}}";
const char* ap_password = "{{AP_PASSWORD}}";
IPAddress local_ip(10, 0, 0, 1);
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 255, 0);
WebServer server(80);

// ---------- Configuración dinámica ----------
#define NUM_SERVOS {{NUM_SERVOS}}
#define STOP_PWM   {{STOP_PWM}}
#define MAX_CW_PWM {{MAX_CW_PWM}}
#define MAX_CCW_PWM {{MAX_CCW_PWM}}
#define MS_PER_DEG {{MS_PER_DEG}}
#define MIN_MOVE_THRESHOLD 0.5
#define RAMP_TIME 50
#define DEADZONE {{DEADZONE}}
#define LED_PIN 2
#define LED_BLINK_DURATION 100
const int PINS[NUM_SERVOS] = { {{SERVO_PINS}} };
#define LOOP_INTERVAL 20

Servo servos[NUM_SERVOS];
bool moving[NUM_SERVOS];
unsigned long stopAt[NUM_SERVOS];
float targetAngle[NUM_SERVOS];
float currentAngle[NUM_SERVOS];
unsigned long ledOffTime = 0;
bool ledState = false;
unsigned long lastLoopTime = 0;
float calibrationFactor = 1.2;
bool debugMode = false;

// ---------- Helpers ----------
void blinkLED() {
  digitalWrite(LED_PIN, HIGH);
  ledState = true;
  ledOffTime = millis() + LED_BLINK_DURATION;
}

void updateLED() {
  if (ledState && millis() >= ledOffTime) {
    digitalWrite(LED_PIN, LOW);
    ledState = false;
  }
}

void stopAll() {
  for (int i = 0; i < NUM_SERVOS; ++i) {
    servos[i].write(STOP_PWM);
    moving[i] = false;
  }
  blinkLED();
  Serial.println("⏹️  Todos los servos detenidos");
}

int calculatePWM(float angleDeg) {
  if (abs(angleDeg) < MIN_MOVE_THRESHOLD) return STOP_PWM;
  int pwm;
  if (angleDeg > 0) {
    pwm = STOP_PWM + DEADZONE + (int)((MAX_CW_PWM - STOP_PWM - DEADZONE) * min(1.0, abs(angleDeg) / 90.0));
  } else {
    pwm = STOP_PWM - DEADZONE - (int)((STOP_PWM - MAX_CCW_PWM - DEADZONE) * min(1.0, abs(angleDeg) / 90.0));
  }
  return constrain(pwm, MAX_CCW_PWM, MAX_CW_PWM);
}

void startMove(int idx, float angleDeg) {
  if (idx < 0 || idx >= NUM_SERVOS) return;
  if (abs(angleDeg) < MIN_MOVE_THRESHOLD) return;

  int pwm = calculatePWM(angleDeg);
  unsigned long duration = (unsigned long)(abs(angleDeg) * MS_PER_DEG * calibrationFactor);

  servos[idx].write(pwm);
  blinkLED();
  moving[idx] = true;
  stopAt[idx] = millis() + duration;
  targetAngle[idx] = currentAngle[idx] + angleDeg;

  Serial.printf("▶️  Servo %d: %s %.1f° (%lu ms)\n",
                idx + 1,
                (angleDeg > 0) ? "↻" : "↺",
                angleDeg,
                duration);
}

void updateMoves() {
  unsigned long now = millis();
  for (int i = 0; i < NUM_SERVOS; ++i) {
    if (moving[i] && now >= stopAt[i]) {
      servos[i].write(STOP_PWM);
      blinkLED();
      moving[i] = false;
      currentAngle[i] = targetAngle[i];
      Serial.printf("✅ Servo %d detenido en %.1f°\n", i + 1, currentAngle[i]);
    }
  }
}

void resetPositions() {
  for (int i = 0; i < NUM_SERVOS; ++i) {
    currentAngle[i] = 0.0;
    targetAngle[i] = 0.0;
  }
  Serial.println("🔄 Posiciones reiniciadas a 0°");
}

// ---------- Comandos ----------
void process_command(String cmd) {
  cmd.trim();
  if (cmd.startsWith("A ")) {
    String values = cmd.substring(2);
    float angle_values[NUM_SERVOS];
    int parsed_count = 0;
    int start = 0;
    for (int i = 0; i < NUM_SERVOS && start < values.length(); i++) {
      int space_pos = values.indexOf(' ', start);
      String value_str;
      if (space_pos == -1) {
        value_str = values.substring(start);
        start = values.length();
      } else {
        value_str = values.substring(start, space_pos);
        start = space_pos + 1;
      }
      if (value_str.length() > 0) {
        angle_values[i] = value_str.toFloat();
        parsed_count++;
      }
    }
    if (parsed_count == NUM_SERVOS) {
      stopAll();
      delay(50);
      for (int i = 0; i < NUM_SERVOS; i++) startMove(i, angle_values[i]);
    } else {
      Serial.printf("❌ A espera %d valores\n", NUM_SERVOS);
    }
  }
  else if (cmd.startsWith("V ")) {
    String values = cmd.substring(2);
    float pwm_values[NUM_SERVOS];
    int parsed_count = 0;
    int start = 0;

    for (int i = 0; i < NUM_SERVOS && start < values.length(); i++) {
      int space_pos = values.indexOf(' ', start);
      String value_str;
      if (space_pos == -1) {
        value_str = values.substring(start);
        start = values.length();
      } else {
        value_str = values.substring(start, space_pos);
        start = space_pos + 1;
      }

      if (value_str.length() > 0) {
        pwm_values[i] = value_str.toFloat();
        parsed_count++;
      }
    }

    if (parsed_count == NUM_SERVOS) {
      for (int i = 0; i < NUM_SERVOS; i++) {
        servos[i].write(constrain((int)pwm_values[i], 0, 180));
      }
      blinkLED();
      Serial.print("✅ PWM directo: ");
      for (int i = 0; i < NUM_SERVOS; i++) {
        Serial.printf("%d ", (int)pwm_values[i]);
      }
      Serial.println();
    } else {
      Serial.printf("❌ V espera %d valores\n", NUM_SERVOS);
    }
  }
  else if (cmd.equalsIgnoreCase("S")) {
    stopAll();
  }
  else if (cmd.equalsIgnoreCase("R")) {
    resetPositions();
  }
  else {
    Serial.println("❓ Comando no reconocido");
  }
}

// ---------- Web Server ----------
void handleRoot() {
  server.send(200, "text/html", index_html);
}

void handleCommand() {
  if (server.hasArg("q")) {
    String cmd = server.arg("q");
    process_command(cmd);
    handleRoot();
  } else {
    server.send(400, "text/plain", "❌ Falta 'q'");
  }
}

{{INDEX_HTML}}

// ---------- Setup ----------
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  lastLoopTime = millis();

  for (int i = 0; i < NUM_SERVOS; ++i) {
    servos[i].attach(PINS[i]);
    moving[i] = false;
    stopAt[i] = 0;
    currentAngle[i] = 0.0;
    targetAngle[i] = 0.0;
  }

  stopAll();

  // WiFi AP + IP
  WiFi.softAPConfig(local_ip, gateway, subnet);
  WiFi.softAP(ap_ssid, ap_password);
  Serial.print("📡 AP iniciado. IP: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/cmd", handleCommand);
  server.begin();
  Serial.printf("🌐 Web server listo. SSID: %s, PASS: %s\n", ap_ssid, ap_password);
}

// ---------- Loop ----------
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    process_command(cmd);
  }
  updateMoves();
  updateLED();
  server.handleClient();
}
