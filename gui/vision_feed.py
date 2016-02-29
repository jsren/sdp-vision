""" Vision Overlay - (c) SDP Team E 2016
    --------------------------------
    Authors: Jake, James Renwick
    Team: SDP Team E
"""

try:
    import cv2
except:
    pass

from config import Configuration

def nothing(x): 
    pass

class GUI:

    def __init__(self, pitch, color_settings, calibration, wrapper):
        self.frame = None
        self.pitch = pitch
        self.color_settings = color_settings
        self.wrapper = wrapper

        self.calibration = calibration
        self.config      = Configuration.read_video_config(create_if_missing=True)

        # create GUI
        # The first numerical value is the starting point for the vision feed
        cv2.namedWindow('frame2')

        # Handle mouse clicks
        cv2.setMouseCallback('frame2', self.on_mouse_event)

        if self.color_settings in [0, "small"]:
            cv2.createTrackbar('bright','frame2',self.config.brightness,255,nothing)
            cv2.createTrackbar('contrast','frame2',self.config.contrast,127,nothing)
            cv2.createTrackbar('color','frame2',self.config.color,255,nothing)
            cv2.createTrackbar('hue','frame2',self.config.hue,30,nothing)
            cv2.createTrackbar('Red Balance','frame2',self.config.red_balance,20,nothing)
            cv2.createTrackbar('Blue Balance','frame2',self.config.blue_balance,20,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',0,1,nothing)

        if self.color_settings in [1, "big"]:
            cv2.createTrackbar('bright','frame2',self.config.brightness,40000,nothing)
            cv2.createTrackbar('contrast','frame2',self.config.contrast,40000,nothing)
            cv2.createTrackbar('color','frame2',self.config.color,100000,nothing)
            cv2.createTrackbar('hue','frame2',self.config.hue,60000,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',0,1,nothing)

    def on_mouse_event(self, event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN:
            #if self.wrapper.color_pick_callback is not None:
                #self.wrapper.color_pick_callback(self.frame[x, y])
            print self.frame[x, y]

    def drawGUI(self, frame):
        self.frame = frame

        if self.color_settings in [0, "small"]:
            attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
        elif self.color_settings in [1, "big"]:
            attributes = ["bright", "contrast", "color", "hue"]
        else:
            raise RuntimeError("StupidTitException: Incorrect color_settings value. Choose from the set [0, small, 1, big]")

        for att in attributes:
            self.config[att] = cv2.getTrackbarPos(att, 'frame2')
        self.config.commit()

    def commit_settings(self):
        for attr in self.config:
            self.config[attr] = cv2.getTrackbarPos(attr, 'frame2')
        Configuration.write_video_config(self.config, self.config.machine_name)


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
