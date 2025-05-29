import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import time
import math

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Layout keyboard
keys = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
    ["Space", "Enter", "Backspace"]
]

# Ukuran tombol
key_w = 80
key_h = 80

last_click_time = 0
click_delay = 1  # detik
last_key = None

# Fungsi menggambar tombol
def draw_keys(img):
    key_positions = []
    start_y = 250
    for row_idx, row in enumerate(keys):
        if row_idx == 3:
            # Baris tombol khusus
            start_x = 180
        else:
            start_x = 100 + row_idx * 40
        for key in row:
            x1 = start_x
            y1 = start_y
            w = key_w * 2 if key in ["Space", "Enter", "Backspace"] else key_w
            x2 = x1 + w
            y2 = y1 + key_h
            key_positions.append((key, (x1, y1, x2, y2)))
            cv2.rectangle(img, (x1, y1), (x2, y2), (50, 50, 50), -1)
            text = key if len(key) == 1 else key[:3]
            cv2.putText(img, text, (x1 + 20, y1 + 55), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            start_x += w + 10
        start_y += key_h + 20
    return key_positions

# Cek apakah kursor di dalam tombol
def is_inside(x, y, box):
    x1, y1, x2, y2 = box
    return x1 < x < x2 and y1 < y < y2

# Hitung jarak antara dua titik
def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

# Kamera dan ukuran frame
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # width
cap.set(4, 720)   # height

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    key_boxes = draw_keys(frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark

            # Ambil koordinat jari telunjuk dan tengah
            index_finger = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_finger = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            x = int(index_finger.x * w)
            y = int(index_finger.y * h)
            x_m = int(middle_finger.x * w)
            y_m = int(middle_finger.y * h)

            # Gambar lingkaran di ujung jari telunjuk
            cv2.circle(frame, (x, y), 10, (0, 255, 255), -1)

            # Cek apakah "klik" (jari telunjuk dan tengah dekat)
            click = distance((x, y), (x_m, y_m)) < 40

            for key, (x1, y1, x2, y2) in key_boxes:
                if is_inside(x, y, (x1, y1, x2, y2)):
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), -1)
                    cv2.putText(frame, key[:3], (x1+20, y1+55), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

                    if click and (time.time() - last_click_time > click_delay):
                        if key == "Space":
                            pyautogui.write(" ")
                        elif key == "Enter":
                            pyautogui.press("enter")
                        elif key == "Backspace":
                            pyautogui.press("backspace")
                        else:
                            pyautogui.write(key.lower())

                        last_click_time = time.time()
                        last_key = key

    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
