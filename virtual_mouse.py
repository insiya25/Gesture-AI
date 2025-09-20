import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui


# Disable fail-safe (not recommended)
pyautogui.FAILSAFE = False

detector = htm.handDetector(maxHands=1)

smoothening = 3
plocX, plocy = 0, 0
curlocX, curlocy = 0, 0

frame_reduction = 50


# getting screen width and height
width_screen, height_screen = pyautogui.size()
width_screen, height_screen

previous_time = 0

cap = cv2.VideoCapture(1)

WIDTH_CAM = 640
HEIGHT_CAM = 480
cap.set(3, WIDTH_CAM)
cap.set(4, HEIGHT_CAM)

while cap.isOpened():
    success, frame = cap.read()
    # 1. find hand landmarks
    frame = detector.findHands(frame)
    lmlist, bbox = detector.findPosition(frame)

    # 2. Get the tip of the index and middle fingers
    if len(lmlist) != 0:
        x1, y1 = lmlist[8][1:]  # 8 is the point for index finger
        x2, y2 = lmlist[12][1:]  # 12 is for middle finger
        # print(x1, y1, x2, y2)

        # 3. Check which fingers are up
        fingers = detector.fingersUp()

        cv2.rectangle(
            frame,
            (frame_reduction, frame_reduction),
            (WIDTH_CAM - frame_reduction, HEIGHT_CAM - frame_reduction),
            (255, 0, 255),
            2,
        )

        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:

            # 5. Convert Coordinates
            x3 = np.interp(
                x1, (frame_reduction, WIDTH_CAM - frame_reduction), (0, width_screen)
            )
            y3 = np.interp(
                y1, (frame_reduction, HEIGHT_CAM - frame_reduction), (0, height_screen)
            )

            # 6. Smoothen Values
            curlocX = plocX + (x3 - plocX) / smoothening
            curlocy = plocy + (y3 - plocy) / smoothening

            # 7. Move Mouse
            pyautogui.moveTo(curlocX, curlocy)
            cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocy = curlocX, curlocy

        # 8. Both index and mid fingers are up: Clicking mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between index and mid finger
            length, frame, lineInfo = detector.findDistance(8, 12, frame)
            # print(length)

            # 10. Click mouse if the distance is short
            if length < 40:
                cv2.circle(
                    frame, (lineInfo[4], lineInfo[5]), 15, (0, 255, 255), cv2.FILLED
                )
                pyautogui.click()

    # 11. Frame Rate
    current_time = time.time()
    fps = 1 / (current_time - previous_time)
    previous_time = current_time
    cv2.putText(
        frame, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3
    )

    # 12. Dislay
    cv2.imshow("image", frame)
    cv2.resizeWindow("image", WIDTH_CAM, HEIGHT_CAM)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
