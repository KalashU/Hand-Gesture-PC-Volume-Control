import cv2
import numpy as np
import time
import HandTMA as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


######################
wCam, hCam = 640, 480
######################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
area = 0
detector = htm.handDetector(detectionCon=0.7, maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
colorVol = (255, 0, 0)


while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])//100
        #print(area)
        if 240 < area < 1000:

            # Find distance between index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)
            print(length)
            # Convert volume

            volBar = np.interp(length, [70, 300], [400, 150])
            volPer = np.interp(length, [70, 300], [0, 100])

            # Reduce resolution
            smoothness = 5
            volPer = smoothness * round(volPer/smoothness)

            # Check finger up
            fingers = detector.fingersUp()
            #print(fingers)
            # If pinky is down set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255, 0, 0)

    # Drawings
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 220, 227), 1)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Vol set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, colorVol, 1)
    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                2, (255, 0, 0), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)
