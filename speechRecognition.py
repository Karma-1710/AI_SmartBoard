import cv2
import os
import math
import mediapipe as mp
import sys
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import speech_recognition as sr
import pyttsx3

width, height = 1280, 720
folderPath = "presentation"

# camera
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# geting the presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
# print(pathImages)

imgNumber = 0
hs, ws = int(120 * 1), int(213 * 1)
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 30
annotations = [[]]
annotationNumber = 0
annotationStart = False

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)


recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio).lower()
        print("You said:", query)
        return query
    except sr.UnknownValueError:
        print("Sorry, I didn't get that.")
        return ""
    except sr.RequestError:
        print("Sorry, I couldn't request results. Please check your internet connection.")
        return ""


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    voice_command = listen()

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if voice_command:
        if "next" in voice_command:
            if imgNumber < len(pathImages) - 1:
                buttonPressed = True
                imgNumber += 1
                annotations = [[]]
                annotationNumber = 0
                speak("Going to next slide.")
            else:
                speak("This is the last slide.")
        elif "previous" in voice_command:
            if imgNumber > 0:
                buttonPressed = True
                imgNumber -= 1
                annotations = [[]]
                annotationNumber = 0
                speak("Going to previous slide.")
            else:
                speak("This is the first slide.")

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        # print(fingers)
        lmList = hand['lmList']

        # indexFinger = lmList[8][0].lmList[8][1]
        xVal = int(np.interp(lmList[8][0], [width // 2, w], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        # direction
        if cy <= gestureThreshold:
            annotationStart = False
            # Left
            if fingers == [1, 0, 0, 0, 0]:
                annotationStart = False
                print("Left")
                if imgNumber > 0:
                    buttonPressed = True
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = 0

            # Right
            if fingers == [0, 0, 0, 0, 1]:
                annotationStart = False
                print("Right")
                if imgNumber < len(pathImages) - 1:
                    buttonPressed = True
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = 0

        # RedPointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotationStart = False

        # drawing
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        # erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber > 0:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True
    else:
        annotationStart = False

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            # buttonDelay = 10
            buttonPressed = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):

            if j != 0:
                cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)

    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w - ws:w] = imgSmall

    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break