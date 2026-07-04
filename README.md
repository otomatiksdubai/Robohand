#  AI Robotic Hand using Computer Vision and Arduino

A real-time AI-powered robotic hand control system using **Python, OpenCV, MediaPipe, Arduino, and Servo Motors**.

This project tracks human hand movements through a webcam and mirrors those movements onto a robotic hand using servo motors in real time.

The system uses AI-based hand tracking to detect finger bending angles and sends servo commands to Arduino through serial communication.

---

#  Features

-> Real-time hand tracking  
-> AI-powered finger detection  
-> Live robotic hand mirroring  
-> Servo motor control using Arduino  
-> Serial communication between Python and Arduino  
-> MediaPipe hand landmark visualization  
-> Thumb movement amplification  
-> Smooth real-time performance  

---

#  Technologies Used

 Technology -> Purpose 

 Python -> Main Programming Language 
 OpenCV -> Webcam & Image Processing 
 MediaPipe ->  AI Hand Tracking 
 NumPy ->  Mathematical Calculations 
 PySerial ->  Serial Communication 
 Arduino -> Servo Motor Control 

---

#  Hardware Required

- Arduino Uno / ESP32
- 5 Servo Motors
- Robotic Hand Structure
- Jumper Wires
- External Power Supply
- Laptop Webcam / USB Camera

---

#  Software Required

Install the following:

- Python 3.10+
- Arduino IDE

Install Python libraries:

```bash
pip install opencv-python mediapipe pyserial numpy
```

---

#  Project Structure

```text
project/
│
├── arm.py
├── README.md
└── Arduino_Code/
```

---

#  How It Works

##  Webcam Captures Hand

The webcam continuously captures live video frames.

---

##  MediaPipe Detects Hand Landmarks

MediaPipe identifies 21 hand landmarks in real time.

---

##  Finger Angles are Calculated

The system calculates finger bending angles using vector mathematics.

---

##  Servo Angles are Generated

Finger bend values are converted into servo motor rotation angles.

---

##  Data is Sent to Arduino

Servo angles are transmitted using serial communication.

---

##  Robotic Hand Mirrors Movement

Arduino receives servo values and moves the robotic fingers accordingly.

---

#  System Architecture

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Tracking
   ↓
Finger Angle Calculation
   ↓
Servo Angle Mapping
   ↓
Serial Communication
   ↓
Arduino
   ↓
Servo Motors
   ↓
Robotic Hand Movement
```

---

#  Finger Mapping

Finger - Servo 

 Pinky - Servo 1 
 Index - Servo 2
 Ring -  Servo 3 
 Middle - Servo 4 
 Thumb - Servo 5 

---

#  Serial Port Configuration

Inside the Python code:

```python
SERIAL_PORT = 'COM6'
BAUD = 115200
```

Change `COM6` to your Arduino serial port if needed.

---

#  Running the Project

## Step 1 — Upload Arduino Code

Upload the Arduino servo control code to your Arduino board.

---

## Step 2 — Connect Hardware

- Connect all servo motors
- Power the servos properly
- Connect Arduino to the PC

---

## Step 3 — Run Python Script

```bash
python arm.py
```

---

## Step 4 — Show Your Hand to Webcam

The robotic hand will start mirroring your finger movements.

Press:

```text
Q
```

to quit the program.

---

#  Hand Tracking Visualization

The system displays:
- Hand skeleton
- Finger servo angles
- Detection status
- Live webcam feed

---

#  Core Concepts Used

- Computer Vision
- AI-based Hand Tracking
- Robotics
- Embedded Systems
- Real-Time Processing
- Serial Communication
- Kinematics

---

#  Future Improvements

- ESP32 Wireless Communication
- Gesture Recognition
- Voice Control
- IoT Integration
- VR Hand Tracking
- Haptic Feedback
- Machine Learning Gesture Prediction

---

#  Example Applications

- Robotics Research
- Prosthetic Hand Systems
- Gesture-Based Automation
- Human-Robot Interaction
- Educational STEM Projects
- VR/AR Interfaces

---

#  Troubleshooting

## Webcam Not Detected

- Check camera permissions
- Verify webcam connection

---

## Serial Port Error

Update:

```python
SERIAL_PORT = 'COM6'
```

with the correct Arduino port.

---

## Servo Jitter

Use:
- external servo power supply
- proper grounding

---

## Hand Not Detected

Improve:
- lighting conditions
- webcam visibility

---

#  Source Code

Main project source:
`arm.py`

Based on:
- OpenCV
- MediaPipe
- Arduino Serial Communication

---

#  Author

Developed as an AI-powered robotics and computer vision project integrating real-time hand tracking with robotic actuation.

---

#  License

This project is open-source and available for educational and research purposes.

---