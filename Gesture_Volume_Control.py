import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math


######################## Pycaw from github ########################
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
# volume.GetVolumeRange()  # this returns the volume range as a tuple which is -65(min) to 0(max)
# volume.SetMasterVolumeLevel(-20.0, None)  # using this we can set the volume
####################################################################


#######################################################
detector = htm.handDetector(detectionCon=0.7)
WIDTH_CAM = 640
HEIGHT_CAM = 480
previous_time = 0

minvol, maxvol, _ = volume.GetVolumeRange()  # unpacking
vol = 0
volume_bar = (
    400  # setting initial value of the bar, 400 is the coordinate when its lowest
)
vol_percentage = 0
#######################################################

cap = cv2.VideoCapture(1)

cap.set(3, WIDTH_CAM)
cap.set(4, HEIGHT_CAM)

while True:
    success, frame = cap.read()

    # find/detect hands using the method below
    frame = detector.findHands(frame)

    # getting landmarks
    lmlist, bbox = detector.findPosition(frame, draw=False)
    # print(lmlist) # printing all the landmarks position

    # Get the tip of the index fingers and thumbs
    if len(lmlist) != 0:
        x0, y0 = lmlist[4][1:]  # 4 for Thumb tip
        x1, y1 = lmlist[8][1:]  # 8 for index finger tip

        # draw circle on tip of the thumb and index finger
        cv2.circle(frame, (x0, y0), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

        # draw line between the two circles
        cv2.line(frame, (x0, y0), (x1, y1), (255, 0, 255), 3)

        # get the center of the line
        centerx, centery = (x0 + x1) // 2, (y0 + y1) // 2

        # draw circle for the center of the line as well
        cv2.circle(frame, (centerx, centery), 15, (255, 0, 255), cv2.FILLED)

        # get the length of the line
        length = math.hypot(x1 - x0, y1 - y0)  # lets say treshold is min 50 and max 300
        # print(length)  # print the length out

        ##########
        # Our line length minimum is 50 and max 250
        # But min volume is -65 to max 0
        # hence, we need to convert the line range using `np.interp()`
        vol = np.interp(
            length,  # the value to convert
            [50, 250],  # line range
            [minvol, maxvol],  # range to convert to
        )
        # print(vol)
        ##########

        # Setting the master volume
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            # change color of the center circle
            cv2.circle(frame, (centerx, centery), 15, (0, 0, 255), cv2.FILLED)
        if length >= 250:
            # change color of the center circle
            cv2.circle(frame, (centerx, centery), 15, (0, 0, 255), cv2.FILLED)

        # we need to display a vol bar so will convert one for that using `np.interp`
        volume_bar = np.interp(
            length,
            [50, 250],
            [
                400,
                150,
            ],  # range to convert to (min is 400 to 150 (this is the coordinate height of the bar) )
        )

        # We also want to display a Volume percentage below the bar so will also do a conversion for that
        vol_percentage = np.interp(
            length, [50, 250], [0, 100]
        )  # this will be 0 ot 100 cuz percentage

    # Now we will create a rectangle bar to display the volumne on the screen as well
    cv2.rectangle(
        frame, (50, 150), (85, 400), (0, 1, 112), 3
    )  # 400 - 150 is the height coordinate of the bar
    cv2.rectangle(frame, (50, int(volume_bar)), (85, 400), (0, 1, 112), cv2.FILLED)

    # Now we will display the Volume percentage
    cv2.putText(
        frame,
        f"{int(vol_percentage)}%",
        (40, 450),
        cv2.FONT_HERSHEY_PLAIN,
        3,
        (0, 1, 112),
        3,
    )

    # Calculate the FPS
    current_time = time.time()
    fps = 1 / (current_time - previous_time)
    previous_time = current_time

    # Display FPS on the frame
    cv2.putText(
        frame,
        str(int(fps)),
        (20, 50),
        cv2.FONT_HERSHEY_PLAIN,
        3,
        (255, 0, 0),
        3,
    )

    cv2.imshow("frame", frame)
    cv2.resizeWindow("frame", WIDTH_CAM, HEIGHT_CAM)

    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
