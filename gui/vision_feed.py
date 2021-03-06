""" Vision Overlay - (c) SDP Team E 2016
    --------------------------------
    Authors: Jake, James Renwick, Linas
    Team: SDP Team E
"""

try:
    import cv2
except:
    pass

from math import radians, cos, sin, isnan
from ..colors import *
from ..config import Configuration
from ..robot_tracker import ROBOT_DISTANCE

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
        self.draw_correction    = False  # Correction crashes things sometimes due to getting out of image bounds

        self.input_mode = 'measure'
        self.p1, self.p2 = None, None

        self.see_ball = False

        # create GUI
        # The first numerical value is the starting point for the vision feed
        #cv2.namedWindow('frame2')

        # Allow easy access from outside
        GUI.instance = self
        self.random_dots = set()



    def on_mouse_event(self, event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.input_mode == 'color_picker':
                self.p1 = (x, y)
                print "Colour:", self.frame[y, x], "@", (x, y)
            if self.input_mode == 'measure':
                if self.p1 is None:
                    self.p1 = (x, y)
                elif self.p2 is None:
                    self.p2 = (x, y)
                    print "Measure: (%d, %d)" %(self.p2[0] - self.p1[0],
                                                self.p2[1] - self.p1[1])
                else:
                    self.p1 = (x, y)
                    self.p2 = None


    def update(self, wrapper):
        # Handle mouse events
        #cv2.setMouseCallback('frame2', self.on_mouse_event)

        try:
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

            # TODO: Dunno what this does?
            # if False and self.input_mode == 'color_picker' and self.p1:
            #     img = self.frame[np.array(self.p1) - np.array([5, 5]),
            #                      np.array(self.p1) + np.array([5, 5])]
            #     print img

            # Draw random circles, requested from elsewhere
            for (pos, color) in self.random_dots:
                cv2.imshow('frame2', cv2.circle(self.frame, pos, 2, BGR_COMMON[color], 2, 0))

            # Draw robot-related stuff
            if self.draw_robots:
                for r in wrapper.robots:
                    if not r.visible: continue

                    clx, cly, x, y = r.coordinates

                    # Resets the robot if it's not been seen for a while.
                    if r.age > 0:
                        # Draw robot circles
                        if not isnan(clx) and not isnan(cly):

                            # Draw robot circle
                            cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)),
                                                            ROBOT_DISTANCE, BGR_COMMON['black'], 2, 0))

                            # Only for debugging circle corrector. Comment out afterwards. ALSO THIS CRASHES HORRIBLY SOMETIMES
                            # due to getting out of bounds when robot is near the edge.
                            if self.draw_correction:
                                from ..robot_tracker import CORRECTION_MAX_DISTANCE, CORRECTION_STEP, CORRECTION_AREA_RADIUS
                                try:
                                    cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)), CORRECTION_AREA_RADIUS,
                                                                    BGR_COMMON['yellow'], 1, 0))
                                except: pass
                                try:
                                    cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)), CORRECTION_STEP,
                                                                    BGR_COMMON['green'], 1, 0))
                                except: pass
                                try:
                                    cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)), CORRECTION_MAX_DISTANCE,
                                                                    BGR_COMMON['blue'], 1, 0))
                                except: pass

                            # Draw Names
                            cv2.imshow('frame2', cv2.putText(self.frame, r.name,
                                                             (int(clx)-15, int(cly)+40),
                                                             cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))


                            # Show centroids of found circles (contours)
                            for val in r.latest_values:
                                cv2.imshow('frame2', cv2.circle(self.frame, (int(val[0]), int(val[1])), 1,
                                                                BGR_COMMON['black'], 1, 0))


                            scale = 1.
                            if r.role == 'enemy':
                                scale = self.wrapper.ENEMY_SCALE
                            elif r.role == 'ally':
                                scale = self.wrapper.ALLY_SCALE
                            elif r.role == 'group9':
                                scale = self.wrapper.GROUP9_SCALE

                            # Draw Grabber zone
                            if r.role == 'enemy':
                                box = cv2.boxPoints(r.grabbing_zone(role=r.role, scale=scale))
                                box = np.int32(box)
                                height, width = self.frame.shape[0:2]
                                # Ellipse parameters
                                radius = 100
                                center = (width / 2, height - 25)
                                axes = (radius, radius)
                                angle = 0
                                startAngle = 180
                                endAngle = 360
                                BLACK = (0, 0, 0)
                                thickness = 10

                            else:
                                box = cv2.boxPoints(r.grabbing_zone(role=r.role, scale=scale))
                                box = np.int32(box)
                                height, width = self.frame.shape[0:2]
                                # Ellipse parameters
                                radius = 100
                                center = (width / 2, height - 25)
                                axes = (radius, radius)
                                angle = 0
                                startAngle = 180
                                endAngle = 360
                                BLACK = (0, 0, 0)
                                thickness = 10



                            # http://docs.opencv.org/modules/core/doc/drawing_functions.html#ellipse
                            #cv2.imshow('frame2', cv2.ellipse(self.frame, center, axes, angle, startAngle, endAngle, BLACK, thickness))

                            cv2.imshow('frame2', cv2.drawContours(self.frame, [box], 0, BGR_COMMON['red'], 1))

                            # Draw robot holding area
                            # box = cv2.boxPoints(r.grabbing_zone(scale=wrapper.BALL_HOLDING_AREA_SCALE))
                            # box = np.int32(box)
                            # #cv2.imshow('frame2', cv2.ellipse(self.frame,(200,200),(80,50),0,180,360,(0,0,255),1))
                            # cv2.imshow('frame2', cv2.drawContours(self.frame, [box], 0, BGR_COMMON['green'], 1))

                            # ball = wrapper.world_objects['ball']
                            # if ball and ball[2]:
                                # if r.is_point_in_grabbing_zone(ball[0], ball[1], scale=1, circular=False):
                                    # print "YYYYEEEEEEEEEEEEEEEEEEESSSSSS :3", r.name
                                #else:
                                    #print "NO. ;("


                            # Draw other zones
                            box = cv2.boxPoints(r.other_zone("left"))
                            box = np.int32(box)
                            cv2.imshow('frame2', cv2.drawContours(self.frame, [box], 0, BGR_COMMON['yellow'], 1))

                            box = cv2.boxPoints(r.other_zone("right"))
                            box = np.int32(box)
                            cv2.imshow('frame2', cv2.drawContours(self.frame, [box], 0, BGR_COMMON['yellow'], 1))

                            box = cv2.boxPoints(r.other_zone("bottom"))
                            box = np.int32(box)
                            cv2.imshow('frame2', cv2.drawContours(self.frame, [box], 0, BGR_COMMON['yellow'], 1))


                            # Draw heading
                            if self.draw_direction:
                                # Write angle in degrees
                                cv2.imshow('frame2', cv2.putText(self.frame, str(int(r.heading)),
                                                                 (int(clx) - 15, int(cly) + 30),
                                                                 cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))

                                cv2.imshow('frame2', cv2.line(self.frame, (int(clx), int(cly)),
                                                              (int(x), int(y)), BGR_COMMON['red'], 2, 0))

                                # Draw heading line
                                angle = r.heading
                                new_x = clx + 30 * cos(radians(angle))
                                new_y = cly + 30 * sin(radians(angle))
                                cv2.imshow('frame2', cv2.line(self.frame, (int(clx), int(cly)),
                                                              (int(new_x), int(new_y)),
                                                              (200, 150, 50), 3, 0))

            self.counter += 1
            ball = wrapper.get_ball_position()

            if self.draw_ball and ball and ball[2]:
                self.x_ball, self.y_ball, self.see_ball = ball
                color = BGR_COMMON['red']
                if self.see_ball == 2:
                    color = BGR_COMMON['dark_red']
                cv2.imshow('frame2', cv2.circle(self.frame, (int(self.x_ball), int(self.y_ball)), 8, color, 2, 0))

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

        #except Exception, e:
        #    print "[ERROR] Exception drawing vision feed:", e.message
        finally: pass

        # Return frame with overlay drawn
        return self.frame
