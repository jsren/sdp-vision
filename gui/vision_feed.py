""" Vision Overlay - (c) SDP Team E 2016
    --------------------------------
    Authors: Jake, James Renwick
    Team: SDP Team E
"""

try:
    import cv2
except:
    pass

from colors import *
from config import Configuration
from math import radians, cos, sin, isnan
from robot_tracker import ROBOT_DISTANCE

def nothing(x): 
    pass

class GUI:

    x_ball_prev = 0
    y_ball_prev = 0
    counter = 0
    x_ball_prev_prev = 0
    y_ball_prev_prev = 0
    x_ball = 0
    y_ball = 0

    def __init__(self, pitch, color_settings, calibration, wrapper):
        self.frame          = None
        self.pitch          = pitch
        self.color_settings = color_settings
        self.wrapper        = wrapper

        self.calibration = calibration
        self.config      = Configuration.read_video_config(create_if_missing=True)

        self.draw_robot     = True
        self.draw_direction = True
        self.draw_ball      = True

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
            print "Colour:", self.frame[x, y], "@", (x, y)


    def update(self, wrapper):
        self.frame = wrapper.frame

        if self.color_settings in [0, "small"]:
            attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
        elif self.color_settings in [1, "big"]:
            attributes = ["bright", "contrast", "color", "hue"]
        else:
            raise RuntimeError("StupidTitException: Incorrect color_settings value. Choose from the set [0, small, 1, big]")

        for att in attributes:
            self.config[att] = cv2.getTrackbarPos(att, 'frame2')
        self.config.commit()

        if wrapper.draw_contours:
            # Draw robot contours
            for color in wrapper.world_contours.get('circles', list()):
                contours = wrapper.world_contours['circles'][color]
                cv2.fillPoly(self.frame, contours, BGR_COMMON[color])
                cv2.drawContours(self.frame, contours, -1, BGR_COMMON['black'], 1)

            # Draw ball contours
            ball_contour = wrapper.world_contours.get('ball')
            cv2.fillPoly(self.frame, ball_contour, BGR_COMMON['red'])
            cv2.drawContours(self.frame, ball_contour, -1, BGR_COMMON['black'], 1)


        # Feed will stop if this is removed and nothing else is shown
        cv2.imshow('frame2', self.frame)

        for r in wrapper.robots:
            if not r.visible: continue

            clx, cly, x, y = r.get_coordinates()
            # TODO: Does age still apply? - jsren
            if r.age > 0:
                # Draw robot circles
                if not isnan(clx) and not isnan(cly):
                    if self.draw_robot:
                        # Draw circle
                        cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)),
                                                        ROBOT_DISTANCE, BGR_COMMON['black'], 2, 0))

                        # Draw Names
                        cv2.imshow('frame2', cv2.putText(self.frame, r.name,
                                                         (int(clx)-15, int(cly)+40),
                                                         cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))

                    if self.draw_direction:
                        # Draw angle in degrees
                        cv2.imshow('frame2', cv2.putText(self.frame, str(int(r.heading)),
                                                         (int(clx) - 15, int(cly) + 30),
                                                     cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))

                        cv2.imshow('frame2', cv2.line(self.frame, (int(clx), int(cly)),
                                                             (int(x), int(y)), BGR_COMMON['red'], 3, 0))

                        # Draw line
                        angle = r.heading
                        new_x = clx + 30 * cos(radians(angle))
                        new_y = cly + 30 * sin(radians(angle))
                        cv2.imshow('frame2', cv2.line(self.frame, (int(clx), int(cly)),
                                                             (int(new_x), int(new_y)),
                                                      (200, 150, 50), 3, 0))

        if self.draw_ball:
            self.counter += 1
            if 'ball' in wrapper.world_objects:
                x_ball, y_ball = wrapper.world_objects['ball']
                cv2.imshow('frame2', cv2.circle(self.frame, (int(x_ball), int(y_ball)), 8, (0, 0, 255), 2, 0))

                if self.counter >= 5:
                    self.x_ball_prev_prev = self.x_ball_prev
                    self.y_ball_prev_prev = self.y_ball_prev
                    self.x_ball_prev      = self.x_ball
                    self.y_ball_prev      = self.y_ball
                    counter = 0

                cv2.imshow('frame2', cv2.arrowedLine(self.frame, (int(self.x_ball_prev_prev), int(self.y_ball_prev_prev)),
                    (abs(int(x_ball+(5*(self.x_ball_prev-self.x_ball_prev_prev)))),
                        abs(int(y_ball+(5*(self.y_ball_prev-self.y_ball_prev_prev))))),
                    (0, 255, 0), 3, 10))


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
