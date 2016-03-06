from vision import Camera
import cv2
import numpy as np

cam = Camera(0)
cam.start_capture()

key = None
i = 0
while key != ord('q'):

    # key = cv2.waitKey(1) & 0xFF
    # frame = cam.get_frame()
    # cv2.imshow('Feed Me', frame)
    #
    # if key == ord('m'):
    #     cv2.imwrite("images/empty_pitch/pitch0/bg%d.png" % i, frame)   # writes image test.bmp to disk
    #     print "saving pitch", i
    #     i += 1
    key = cv2.waitKey(1) & 0xFF

    frame = cam.get_frame()

    #cv2.imshow("I'm old.", frame)
    z = frame.copy()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    colors = []
    for frame in list(cv2.split(frame)):
        ### Transformations
        kernel_val = 3
        kernel = np.ones((kernel_val,kernel_val),np.uint8)#
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(kernel_val,kernel_val))
        # erode
        # frame = cv2.erode(frame,kernel,iterations = 1)

        # dilate
        # frame = cv2.dilate(frame,kernel,iterations = 1)

        # opening == erode -> dilute
        # frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)

        # closing == dilute -> erode
        frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)

        # morphological gradient == outlines - nothing good
        # frame = cv2.morphologyEx(frame, cv2.MORPH_GRADIENT, kernel)

        # top hat == difference between opening and original image - might be useful for kernel values > 9
        # frame = cv2.morphologyEx(frame, cv2.MORPH_TOPHAT, kernel)

        # black hat == difference between closing and original image - useless. Just produces lame outlines
        # frame = cv2.morphologyEx(frame, cv2.MORPH_BLACKHAT, kernel)

        colors.append(frame)

    frame = cv2.merge(tuple(colors))




    ###
    cv2.imshow("output", np.vstack([frame, z]))




    # frame = cam.get_frame()
    # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # CV_THRESH_BINARY = 0
    # retval, frame = cv2.threshold(frame, 100, 255, CV_THRESH_BINARY)
    #
    #
    # el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # frame = cv2.dilate(frame, el, iterations=1)
    # cv2.imshow('Very Transform.', frame)
    #
    # cv2.imwrite("dilated.png", image)
    #
    # contours, hierarchy = cv2.findContours(
    #     image,
    #     cv2.cv.CV_RETR_LIST,
    #     cv2.cv.CV_CHAIN_APPROX_SIMPLE
    # )
    #
    # drawing = cv2.imread("test.jpg")
    #
    # centers = []
    # radii = []
    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #
    #     # there is one contour that contains all others, filter it out
    #     if area > 500:
    #         continue
    #
    #     br = cv2.boundingRect(contour)
    #     radii.append(br[2])
    #
    #     m = cv2.moments(contour)
    #     center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
    #     centers.append(center)
    #
    # print("There are {} circles".format(len(centers)))
    #
    # radius = int(np.average(radii)) + 5
    #
    # for center in centers:
    #     cv2.circle(drawing, center, 3, (255, 0, 0), -1)
    #     cv2.circle(drawing, center, radius, (0, 255, 0), 1)
    #
    # cv2.imwrite("drawing.png", drawing)

cam.stop_capture()