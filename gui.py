""" Vision GUI - (c) SDP Team E 2016
    --------------------------------
    Authors:
    Team: SDP Team E
"""

import cv2

from config import Configuration


def nothing(x): 
    pass

class GUI:

    def __init__(self, pitch):
        self.frame = None
        self.pitch = pitch

        self.config = Configuration.read_video_config(create_if_missing=True)

        # create GUI
        # The first numerical value is the starting point for the vision feed
        if pitch == 0:
            cv2.namedWindow('frame2')
            cv2.createTrackbar('bright','frame2',180,255,nothing)
            cv2.createTrackbar('contrast','frame2',120,127,nothing)
            cv2.createTrackbar('color','frame2',80,255,nothing)
            cv2.createTrackbar('hue','frame2',5,30,nothing)
            cv2.createTrackbar('Red Balance','frame2',5,20,nothing)
            cv2.createTrackbar('Blue Balance','frame2',0,20,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',1,1,nothing)

        if pitch == 1:
            cv2.namedWindow('frame2')
            cv2.createTrackbar('bright','frame2',23000,40000,nothing)
            cv2.createTrackbar('contrast','frame2',28000,40000,nothing)
            cv2.createTrackbar('color','frame2',65000,100000,nothing)
            cv2.createTrackbar('hue','frame2',38000,60000,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',1,1,nothing)



    def drawGUI(self):
        if self.pitch == 0:
            attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
        elif self.pitch == 1:
            attributes = ["bright", "contrast", "color", "hue"]
        else:
            raise RuntimeError("StupidTitException: Incorrect pitch number")

        for att in attributes:
            self.config[att] = cv2.getTrackbarPos(att, 'frame2')
        self.config.commit()


    def warp_image(self, frame):
        # TODO: this might work in gui, but are the blur values saved anywhere?
        # TODO: implement blur value variations
        """
        Creates trackbars and applies frame preprocessing for functions that actually require a frame,
        instead of setting the video device options
        :param frame: frame
        :return: preprocessed frame
        """
        blur = cv2.getTrackbarPos('Gaussian blur', 'frame2')

        if blur >= 1:
            if blur % 2 == 0:
                blur += 1
            frame = cv2.GaussianBlur(frame, (121, 121), 0)

        return frame
