import cv2
import time

cap = cv2.VideoCapture(0)
print("cap = {}".format(cap))
time.sleep(1.000)  # Make sure, you need to give time for MS Windows to initialize Camera

if cap is None or not (cap.isOpened()):
    print('Could not open video device')
    exit()

while(True):
    # Capture frame-by-frame

    ret, frame = cap.read()

    # Display the resulting frame

    cv2.imshow('preview',frame)

    #Waits for a user input to quit the application

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break