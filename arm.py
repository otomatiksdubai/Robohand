import cv2
import mediapipe as mp
import serial
import numpy as np
import time
from threading import Event

# =========================
# ARDUINO SERIAL SETTINGS
# =========================

SERIAL_PORT = "COM10"  # Change if needed
BAUD = 115200

# =========================
# SERVO ORDER
# =========================
# Python sends angles in this order:
# Thumb, Index, Middle, Ring, Pinky

FINGER_ORDER = ["thumb", "index", "middle", "ring", "pinky"]

# Open and close angles for each finger:
# Order: Thumb, Index, Middle, Ring, Pinky
#
# If any finger moves opposite, swap that finger's OPEN and CLOSE value.

OPEN_ANGLES = [180, 180, 0, 180, 0]
CLOSE_ANGLES = [0, 0, 180, 0, 180]

# =========================
# MEDIAPIPE LANDMARKS
# =========================

FINGER_LM = {
    "thumb": (2, 3, 4),
    "index": (5, 6, 8),
    "middle": (9, 10, 12),
    "ring": (13, 14, 16),
    "pinky": (17, 18, 20),
}


def calc_angle(lm, a, b, c):
    pa = np.array([lm[a].x, lm[a].y, lm[a].z])
    pb = np.array([lm[b].x, lm[b].y, lm[b].z])
    pc = np.array([lm[c].x, lm[c].y, lm[c].z])

    v1 = pa - pb
    v2 = pc - pb

    cos_a = np.dot(v1, v2) / ((np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cos_a, -1.0, 1.0)))

    return float(angle)


def connect_arduino(serial_port=SERIAL_PORT, baud=BAUD):
    print(f"Connecting to Arduino on {serial_port}...")

    try:
        ser = serial.Serial(serial_port, baud, timeout=1)
        time.sleep(2)
        print("Arduino connected!")
        return ser
    except Exception as e:
        print("Arduino not connected; continuing without serial control.")
        print(e)
        return None


def init_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")

    return cap


def init_hands():
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.65,
    )
    return mp_hands, mp_draw, hands


def run_hand_tracking(stop_event=None, frame_callback=None, show_window=False, serial_port=SERIAL_PORT, baud=BAUD):
    if stop_event is None:
        stop_event = Event()

    ser = connect_arduino(serial_port, baud)
    cap = init_camera()
    mp_hands, mp_draw, hands = init_hands()

    last_send = 0
    send_every = 0.04
    smooth_angles = OPEN_ANGLES.copy()

    print("Running...")
    print("Show your hand to the camera.")
    print("Press Q to quit or use the Stop button in the web page.")

    try:
        while not stop_event.is_set():
            ret, frame = cap.read()

            if not ret:
                print("Failed to read camera")
                continue

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            target_angles = OPEN_ANGLES.copy()
            hand_found = False

            if result.multi_hand_landmarks:
                hand_found = True

                hand = result.multi_hand_landmarks[0]
                lm = hand.landmark

                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                for i, finger in enumerate(FINGER_ORDER):
                    a, b, c = FINGER_LM[finger]

                    bend = calc_angle(lm, a, b, c)

                    servo_angle = int(np.interp(bend, [45, 170], [CLOSE_ANGLES[i], OPEN_ANGLES[i]]))
                    servo_angle = int(np.clip(servo_angle, 0, 180))

                    if finger == "thumb":
                        servo_angle = OPEN_ANGLES[i] - ((OPEN_ANGLES[i] - servo_angle) * 2)
                        servo_angle = int(np.clip(servo_angle, 0, 180))

                    target_angles[i] = servo_angle

                    tip_x = int(lm[c].x * frame.shape[1])
                    tip_y = int(lm[c].y * frame.shape[0])

                    cv2.putText(
                        frame,
                        f"{finger}: {servo_angle}",
                        (tip_x - 40, tip_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (0, 255, 0),
                        1,
                    )
            else:
                target_angles = OPEN_ANGLES.copy()

            for i in range(5):
                smooth_angles[i] = int((smooth_angles[i] * 0.7) + (target_angles[i] * 0.3))

            if time.time() - last_send > send_every and ser is not None:
                cmd = ",".join(str(a) for a in smooth_angles) + "\n"

                try:
                    ser.write(cmd.encode())
                except Exception as e:
                    print("Serial error:", e)

                last_send = time.time()

            if hand_found:
                status = "Hand detected"
                color = (0, 255, 0)
            else:
                status = "No hand - opening"
                color = (0, 80, 255)

            cv2.putText(
                frame,
                status,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

            cv2.putText(
                frame,
                "AI Robotic Hand | Press Q to quit",
                (10, 460),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (180, 180, 180),
                1,
            )

            if frame_callback is not None:
                frame_callback(frame.copy(), status, hand_found)

            if show_window:
                cv2.imshow("AI Robotic Hand", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        if ser is not None:
            try:
                ser.write(("0,0,0,0,0\n").encode())
                time.sleep(0.2)
            except Exception:
                pass
            ser.close()

        cap.release()
        if show_window:
            cv2.destroyAllWindows()

        print("Stopped.")


if __name__ == "__main__":
    run_hand_tracking(show_window=True)
