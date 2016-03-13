

from vision import Camera
import cv2

cam = Camera(0)
cam.start_capture()
frame = cam.get_frame()
background_sub = None
while cv2.waitKey(1) & 0xFF != ord('q'):
    frame = cam.get_frame()
    frame = cv2.blur(frame, (2,2))
    if background_sub is not None:
        bg_mask = background_sub.apply(frame)
    else:
        background_sub = cv2.createBackgroundSubtractorMOG2()
        bg_mask = background_sub.apply(frame)
    frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame2[:, :, 1] = cv2.equalizeHist(frame2[:, :, 1])
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_HSV2BGR);

    cv2.imshow('Fucking normie', frame2)
    cv2.imshow('BG Scrub',bg_mask)
    cv2.imshow('Fucking Hipster Trash', frame)

cam.stop_capture()

