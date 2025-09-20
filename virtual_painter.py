import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm

#######################
brushThickness = 25
eraserThickness = 100
########################


# Define Headers folder path
folderPath = "virtualPaint_Headers"

# going through each image path and appending them
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f"{folderPath}/{imPath}")
    overlayList.append(image)
print(len(overlayList))

# display the first image as default
header = overlayList[0]

# store color (whenever a brush is selected the color will change)
drawColor = (255, 255, 255)

cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

# instantiating our detector
detector = htm.handDetector(detectionCon=0.65, maxHands=1)

# these is x previous and y previous (prev coordinates of both axis)
xp, yp = 0, 0

# this will be the canvas on which we will draw
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

while True:

    # 1. Import image
    success, img = cap.read()
    # img = cv2.flip(img, 1)  # flipping the image (optional)

    # 2. Find Hand Landmarks
    img = detector.findHands(img)

    # Get all the landmarks position
    lmList, bbox = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # print(lmList)

        # tip of index and middle fingers
        x1, y1 = lmList[8][1:]  # 8 is tip of index finger
        x2, y2 = lmList[12][1:]  # 12 is tip of middle finger

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)

        # 4. If Selection Mode - Two finger are up
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0
            print("Selection Mode")

            # Checking for clicks
            if y1 < 120:
                if 223 < x1 < 309:
                    header = overlayList[0]
                    drawColor = (255, 255, 255)
                elif 348 < x1 < 434:
                    header = overlayList[1]
                    drawColor = (49, 49, 255)
                elif 473 < x1 < 559:
                    header = overlayList[2]
                    drawColor = (255, 182, 56)
                elif 598 < x1 < 684:
                    header = overlayList[3]
                    drawColor = (99, 191, 0)
                elif 723 < x1 < 809:
                    header = overlayList[4]
                    drawColor = (196, 102, 255)
                elif 848 < x1 < 934:
                    header = overlayList[5]
                    drawColor = (89, 222, 255)
                elif 973 < x1 < 1059:
                    header = overlayList[6]
                    drawColor = (235, 23, 94)
                elif 1098 < x1 < 1280:
                    header = overlayList[7]
                    drawColor = (0, 0, 0)
            # draw rectangle if selection mode
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        # 5. If Drawing Mode - Index finger is up
        if fingers[1] and fingers[2] == False:

            # draw circle if drawing mode
            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)

            print("Drawing Mode")

            if xp == 0 and yp == 0:
                xp, yp = x1, y1  # draw point at the start

            # if color is black (meaning if its eraser)
            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
            # else if its not the eraser
            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp, yp = x1, y1

            # # Clear Canvas when all fingers are up
            # if all (x >= 1 for x in fingers):
            #     imgCanvas = np.zeros((720, 1280, 3), np.uint8)

    ################################### LOGIC COMBINING IMAGE AND THE CANVA ###################################
    # first creating a gray image (basically converting `imgCanvas` to gray image)
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)

    # converting it to binary image and inverse it
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

    # convert back to BGR
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    # adding our original image with the inverse image
    img = cv2.bitwise_and(img, imgInv)  # using AND operation
    img = cv2.bitwise_or(img, imgCanvas)  # using OR operation

    ############################################################################################################

    # Setting the header image
    img[0:120, 0:1280] = (
        header  # height is from 0 to 120 and width 0 to 1280 (thats our headers size)
    )

    # blending `img` and `imgCanvas` together (dont need to do it since we are already combining it using the logic above)
    # img = cv2.addWeighted(img,0.5,imgCanvas,0.5,0)

    cv2.imshow("Image", img)
    # cv2.imshow("Canvas", imgCanvas)
    # cv2.imshow("Inv", imgInv)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
