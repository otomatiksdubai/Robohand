#include <Servo.h>

Servo fingers[5];

// Servo order used by Python:
// Thumb, Index, Middle, Ring, Pinky
//
// Your actual wiring:
// Pin 7 = Thumb
// Pin 4 = Index
// Pin 6 = Middle
// Pin 3 = Ring
// Pin 5 = Pinky

int pins[5] = {7, 4, 6, 3, 5};

int currentAngles[5] = {180, 180, 0, 180, 0};

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < 5; i++) {
    fingers[i].attach(pins[i]);
    fingers[i].write(currentAngles[i]);
  }

  delay(500);
}

void loop() {
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    if (line.length() < 5) {
      return;
    }

    int angles[5];
    int index = 0;
    int start = 0;

    for (int i = 0; i <= line.length(); i++) {
      if (line[i] == ',' || i == line.length()) {
        if (index < 5) {
          angles[index] = constrain(line.substring(start, i).toInt(), 0, 180);
          index++;
          start = i + 1;
        }
      }
    }

    if (index == 5) {
      for (int i = 0; i < 5; i++) {
        currentAngles[i] = angles[i];
        fingers[i].write(currentAngles[i]);
      }
    }
  }
}