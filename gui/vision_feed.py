""" Vision Overlay - (c) SDP Team E 2016
    --------------------------------
    Authors: Jake, James Renwick, Linas
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

from Tkinter import *

import numpy as np
def nothing(x): 
    pass

class GUI:

    counter = 0
    x_ball_prev = 0
    y_ball_prev = 0
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

        self.draw_robots        = True
        self.draw_direction     = True
        self.draw_ball          = True
        self.draw_ball_velocity = True
        self.draw_contours      = True
        self.draw_correction    = True

        # create GUI
        # The first numerical value is the starting point for the vision feed
        #cv2.namedWindow('frame2')

        # Handle mouse clicks
        #cv2.setMouseCallback('frame2', self.on_mouse_event)


    def on_mouse_event(self, event, x, y, *_):
        pass
        # if event == cv2.EVENT_LBUTTONDOWN:
        #     print "Colour:", self.frame[x, y], "@", (x, y)


    def update(self, wrapper):

        self.frame = wrapper.frame

        if self.draw_contours:
            # Draw robot contours
            for color in wrapper.world_contours.get('circles', list()):
                contours = wrapper.world_contours['circles'][color]
                cv2.fillPoly(self.frame, contours, BGR_COMMON[color])
                cv2.drawContours(self.frame, contours, -1, BGR_COMMON['black'], 1)

            # Draw ball contours
            ball_contour = wrapper.world_contours.get('ball')
            cv2.fillPoly(self.frame, ball_contour, BGR_COMMON['red'])
            cv2.drawContours(self.frame, ball_contour, -1, BGR_COMMON['black'], 1)

        # Draw frame
        cv2.imshow('frame2', self.frame)

        if self.draw_robots:
            for r in wrapper.robots:
                if not r.visible: continue

                clx, cly, x, y = r.get_coordinates()

                # Resets the robot if it's not been seen for a while.
                if r.age > 0:
                    # Draw robot circles
                    if not isnan(clx) and not isnan(cly):

                        # Draw circle
                        cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)),
                                                        ROBOT_DISTANCE, BGR_COMMON['black'], 2, 0))

                        # Only for debugging circle corrector. Comment out afterwards. ALSO THIS CRASHES HORRIBLY SOMETIMES
                        if self.draw_correction:
                            from robot_tracker import CORRECTION_MAX_DISTANCE, CORRECTION_STEP, CORRECTION_AREA_RADIUS
                            cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)), CORRECTION_AREA_RADIUS,
                                                            BGR_COMMON['yellow'], 1, 0))
                            cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)), CORRECTION_STEP,
                                                            BGR_COMMON['green'], 1, 0))
                            cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)), CORRECTION_MAX_DISTANCE,
                                                            BGR_COMMON['blue'], 1, 0))

                        # Draw Names
                        cv2.imshow('frame2', cv2.putText(self.frame, r.name,
                                                         (int(clx)-15, int(cly)+40),
                                                         cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))


                        cv2.imshow('frame2', cv2.polylines(self.frame, r.get_other_coordinates(), True,
                                                           BGR_COMMON['black'], 1))

                        for val in r.get_latest_values():
                            cv2.imshow('frame2', cv2.circle(self.frame, (int(val[0]), int(val[1])), 1,
                                                        BGR_COMMON['red'], 2, 0))


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

        self.counter += 1
        if 'ball' in wrapper.world_objects:
            self.x_ball, self.y_ball = wrapper.world_objects['ball']

            if self.draw_ball:
                cv2.imshow('frame2', cv2.circle(self.frame, (int(self.x_ball), int(self.y_ball)), 8, (0, 0, 255), 2, 0))

            if self.counter % 5 == 0:
                self.x_ball_prev_prev = self.x_ball_prev
                self.y_ball_prev_prev = self.y_ball_prev
                self.x_ball_prev      = self.x_ball
                self.y_ball_prev      = self.y_ball

            if self.draw_ball_velocity:
                cv2.imshow('frame2', cv2.arrowedLine(self.frame, (int(self.x_ball_prev_prev), int(self.y_ball_prev_prev)),
                    (abs(int(self.x_ball+(5*(self.x_ball_prev-self.x_ball_prev_prev)))),
                        abs(int(self.y_ball+(5*(self.y_ball_prev-self.y_ball_prev_prev))))),
                                                     (0,255,0), 3, 10))




    def warp_image(self, frame):
        # TODO: this might work in gui, but are the blur values saved anywhere?
        # TODO: implement blur value variations
        """
        Creates trackbars and applies frame preprocessing for functions that actually require a frame,
        instead of setting the video device options
        :param frame: frame
        :return: preprocessed frame
        """
       # blur = cv2.getTrackbarPos('Gaussian blur', 'frame2')

        #if blur >= 1:
        #    if blur % 2 == 0:
        #        blur += 1
        #    frame = cv2.GaussianBlur(frame, (121, 121), 0)

        return frame
