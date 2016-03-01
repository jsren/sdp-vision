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

        # create GUI
        # The first numerical value is the starting point for the vision feed
        cv2.namedWindow('frame2')

        # Handle mouse clicks
        cv2.setMouseCallback('frame2', self.on_mouse_event)

        self.selector_frame = LabelFrame(self, text="Camera Settings")
        self.selector_frame.grid(row=0, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self._vars = list()

        if self.color_settings in [0, "small"]:

             for att in self.config:
                var = DoubleVar(self)
                self._vars.append(var)

                Scale(self.selector_frame, variable=att,
                    to=Configuration.video_settings_max.small[att], orient=HORIZONTAL, label=att.title(),
                    length=300).pack(anchor=W)


            #cv2.createTrackbar('bright','frame2',self.config.brightness,255,nothing)
            #cv2.createTrackbar('contrast','frame2',self.config.contrast,127,nothing)
            #cv2.createTrackbar('color','frame2',self.config.color,255,nothing)
            #cv2.createTrackbar('hue','frame2',self.config.hue,30,nothing)
            #cv2.createTrackbar('Red Balance','frame2',self.config.red_balance,20,nothing)
            #cv2.createTrackbar('Blue Balance','frame2',self.config.blue_balance,20,nothing)
            #cv2.createTrackbar('Gaussian blur','frame2',0,1,nothing)


        if self.color_settings in [1, "big"]:

            for att in self.config:
                var = DoubleVar(self)
                self._vars.append(var)

                Scale(self.selector_frame, variable=att,
                    to=Configuration.video_settings_max.big[att], orient=HORIZONTAL, label=att.title(),
                    length=300).pack(anchor=W)


            #cv2.createTrackbar('bright','frame2',self.config.brightness,40000,nothing)
            #cv2.createTrackbar('contrast','frame2',self.config.contrast,40000,nothing)
            #cv2.createTrackbar('color','frame2',self.config.color,100000,nothing)
            #cv2.createTrackbar('hue','frame2',self.config.hue,60000,nothing)
            #cv2.createTrackbar('Gaussian blur','frame2',0,1,nothing)

        self.button_frame = Frame(self)
        self.button_frame.grid(row=1, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        Button(self.button_frame, text="Write Configurations", command=self.commit_settings,
               padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Reload from File", command=self.reload_config,
                padx=10, pady=10, width=15).pack(side=LEFT)

        #Button(self.button_frame, text="Revert to Default", command=self.revert_default,
                #padx=10, pady=10, width=15).pack(side=LEFT)

        #Button(self.button_frame, text="Quit", command=self.close,
                #padx=10, pady=10, width=15).pack(side=RIGHT)



    def on_mouse_event(self, event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN:
            print "Colour:", self.frame[x, y], "@", (x, y)

    def update(self, wrapper):

        self.frame = wrapper.frame

        """
        if self.color_settings in [0, "small"]:
             #attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
             self.config.bright =  self.bright.get()
             self.config.contrast =  self.contrast.get()
             self.config.color =  self.color.get()
             self.config.hue =  self.hue.get()
             self.config.red_balance = self.red_balance.get()
             self.config.blue_balance = self.blue_balance.get()

        elif self.color_settings in [1, "big"]:
            #attributes = ["bright", "contrast", "color", "hue"]
            self.config.bright =  self.bright.get()
            self.config.contrast =  self.contrast.get()
            self.config.color =  self.color.get()
            self.config.hue =  self.hue.get()


        else:
            raise RuntimeError("StupidTitException: Incorrect color_settings value. "
                               "Choose from the set [0, small, 1, big]")
        """

        for att in self._vars:
            self.config[att] = self.att.get()
        self.config.commit()


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
                # TODO: Does age still apply? - jsren

                # TODO: Yes, it resets the robot if it's not been seen for a while.
                # TODO: Otherwise we'd have a black circle stuck somewhere on the field. With old values.
                # TODO: Unless you're passing in None sometimes, which I might have seen somewhere. - linas
                if r.age > 0:
                    # Draw robot circles
                    if not isnan(clx) and not isnan(cly):

                        # Draw circle
                        cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)),
                                                        ROBOT_DISTANCE, BGR_COMMON['black'], 2, 0))

                        # Draw Names
                        cv2.imshow('frame2', cv2.putText(self.frame, r.name,
                                                         (int(clx)-15, int(cly)+40),
                                                         cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))


                        cv2.imshow('frame2', cv2.polylines(self.frame, r.get_other_coordinates(), True,
                                                           BGR_COMMON['black'], 1))

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




    def reload_config(self):
        video_settings = Configuration.read_calibration(self.config.machine_name)
        for setting in video_settings:
            self.config[setting] = video_settings[setting]

        self.config.commit()

        pass
    
    def commit_settings(self):
        for attr in self._vars:
            self.config[attr] = self.attr.get()
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
       # blur = cv2.getTrackbarPos('Gaussian blur', 'frame2')

        #if blur >= 1:
        #    if blur % 2 == 0:
        #        blur += 1
        #    frame = cv2.GaussianBlur(frame, (121, 121), 0)

        return frame
