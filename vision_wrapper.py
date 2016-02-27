from copy import deepcopy
from math import radians, cos, sin, isnan

import cv2
import numpy as np

from colors import *
from gui import GUI
from preprocessing.preprocessing import Preprocessing
from robot_tracker import ROBOT_DISTANCE
from util import RobotInstance, tools
from vision import Vision, Camera
from config import Configuration, Calibration

x_ball_prev = 0
y_ball_prev = 0
counter = 0
x_ball_prev_prev = 0
y_ball_prev_prev = 0
x_ball = 0
y_ball = 0

class VisionWrapper:
    """
    Class that handles vision

    """

    def __init__(self, pitch, our_side, robot_details, draw_GUI=False):
        """
        Entry point for the SDP system.

        Params:
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] colour                 The colour of our teams plates
            [string] our_side               the side we're on - 'left' or 'right'
            [int] video_port                port number for the camera

            [boolean] draw_GUI              Does not draw the normal image to leave space for GUI.
                                            Also forces the trackers to return circle contour positons in addition to robot details.
        Fields
            pitch
            camera
            calibration
            vision
            postporcessing
            color
            side
            preprocessing
            model_positions
            regular_positions
        """
        pitch = int(pitch)
        assert pitch in [0, 1]

        self.pitch = pitch

        # Set up camera for frames
        self.camera = Camera(port=0, pitch=pitch)
        self.camera.start_capture()
        self.frame = self.camera.get_frame()
        center_point = self.camera.get_adjusted_center(self.frame)

        # Set up vision

        # Get machine-specific calibration
        self.calibration = Configuration.read_calibration(create_if_missing=True)

        self.draw_GUI = draw_GUI
        self.gui = None
        if draw_GUI:
            self.gui = GUI(self.pitch)

        # Draw various things on the image
        self.draw_direction = True
        self.draw_robot = True
        self.draw_contours = True
        self.draw_ball = True
        self.vision = Vision(
            pitch=pitch, frame_shape=self.frame.shape,
            frame_center=center_point, calibration=self.calibration,
            return_circle_contours=draw_GUI)

        #self.

        # Set up preprocessing and postprocessing
        # self.postprocessing = Postprocessing()
        self.preprocessing = Preprocessing()

        self.side = our_side

        self.frameQueue = []

        # Initialize robots

        self.ball = []
        self.robots = []
        for r_name in robot_details.keys():
            self.robots.append(RobotInstance(r_name,
                                             robot_details[r_name]['main_colour'],
                                             robot_details[r_name]['side_colour']))

    def get_robots_raw(self):
        return [(r.name, np.mean(r.x), np.mean(r.y), r.get_robot_heading())
                for r in self.robots]

    def get_robot_position(self, robot_name):
        for r in self.robots:
            if r.name == robot_name:
                return np.mean(r.x), np.mean(r.y)
            # Team 10:
            # if r.name == robot_name and r.is_present():
            #     return np.array(r.get_coordinates()[:2])

    def get_circle_position(self, robot_name):
        for r in self.robots:
            if r.name == robot_name:
                return r.side_x, r.side_y
            # Team 10
            # if r.name == robot_name and r.is_present():
            #     return np.array(r.get_coordinates()[2:4])

    def get_ball_position(self):
        if 'x' in self.regular_positions.keys():
            return self.regular_positions['x'], self.regular_positions['y']
        # Team 10
        # def get_ball_position(self):
        # if 'x' in self.regular_positions and self.regular_positions['x'] is not None:
        #     return np.array([self.regular_positions['x'],
        #                      self.regular_positions['y']])

    def get_robot_direction(self, robot_name):
        for r in self.robots:
            if r.name == robot_name:
                return r.get_robot_heading()

    def do_we_have_ball(self, robot_name):
        for r in self.robots:
            if r.name == robot_name:
                if 'x' in self.regular_positions.keys():
                    ball_x = self.regular_positions['x']
                    ball_y = self.regular_positions['y']
                    robot_x = np.mean(r.x)
                    robot_y = np.mean(r.y) 
                    #print robot_x, robot_y, ball_x, ball_y
                    if r.get_robot_heading() < 90:
                        if (robot_x-10 < ball_x < robot_x+30 and robot_y-10 < ball_y < robot_y+30):
                            return True
                        else:
                            return False

                    elif (r.get_robot_heading() >= 90 and r.get_robot_heading() < 180):
                        if robot_x-30 < ball_x < robot_x+10 and robot_y-10 < ball_y < robot_y+30:
                            return True
                        else:
                            return False

                    elif (r.get_robot_heading() >= 180 and r.get_robot_heading() < 270):
                        if robot_x-30 < ball_x < robot_x+10 and robot_y-30 < ball_y < robot_y+10:
                            return True
                        else:
                            return False

                    elif (r.get_robot_heading() >= 270 and r.get_robot_heading() < 360):
                        if robot_x-10 < ball_x < robot_x+30 and robot_y-30 < ball_y < robot_y+10:
                            return True
                        else:
                            return False
                 

    def change_drawing(self, key):
        """
        Toggles drawing of contours, heading directions, robot positions and ball tracker
        Usage:
            * 'b' for ball tracker
            * 'n' for contours
            * 'j' for robot_tracker
            * 'i' for heading direction
        :param key: keypress
        :return: nothing
        """
        if key == ord('b'):
            self.draw_ball = not self.draw_ball
        elif key == ord('n'):
            self.draw_contours = not self.draw_contours
        elif key == ord('j'):
            self.draw_robot = not self.draw_robot
        elif key == ord('i'):
            self.draw_direction = not self.draw_direction

    def get_circle_contours(self):
        """
        Careful! Does not return x and y values. Call minimum bounding circles if proper circle locations are required.
        Or look at dem fish http://docs.opencv.org/2.4/doc/tutorials/imgproc/shapedescriptors/find_contours/find_contours.html
        :return: [Contours]
        """
        if 'circles' in self.regular_positions:
            return self.regular_positions['circles']


    def update(self):
        """
        Gets this frame's positions from the vision system.
        """
        global x_ball_prev
        global y_ball_prev
        global y_ball_prev_prev
        global x_ball_prev_prev
        global counter
        global x_ball
        global y_ball

        self.frame = self.camera.get_frame()

        # Apply preprocessing methods toggled in the UI
        self.preprocessed = self.preprocessing.run(self.frame, self.preprocessing.options)
        self.frame = self.preprocessed['frame']
        if 'background_sub' in self.preprocessed:
            cv2.imshow('bg sub', self.preprocessed['background_sub'])

        # Find object positions
        # model_positions have their y coordinate inverted
        # self.model_positions, self.regular_positions = self.vision.locate(self.frame)
        self.regular_positions = self.vision.locate1(self.frame)
        # self.model_positions = self.postprocessing.analyze(self.model_positions)


        # Updates the robot coordinates
        if self.regular_positions['robot_coords']:
            for r_data in self.regular_positions['robot_coords']:
                for robot in self.robots:
                    if robot.update(r_data['clx'], r_data['cly'],
                                    r_data['main_color'], r_data['side_color'], r_data['x'], r_data['y']):
                        break



        if self.draw_GUI:
            self.frame = self.gui.warp_image(self.frame)

            # Draw contours found
            if self.draw_contours:
                # Draw robot contours
                for color in self.regular_positions.get('circles'):
                    contours = self.regular_positions['circles'][color]
                    cv2.fillPoly(self.frame, contours, BGR_COMMON[color])
                    cv2.drawContours(self.frame, contours, -1, BGR_COMMON['black'], 1)

                # Draw ball contours
                ball_contour = self.regular_positions.get('ball_contour')
                cv2.fillPoly(self.frame, ball_contour, BGR_COMMON['red'])
                cv2.drawContours(self.frame, ball_contour, -1, BGR_COMMON['black'], 1)


        # Feed will stop if this is removed and nothing else is shown
        cv2.imshow('frame2', self.frame)

        for r in self.robots:
            if not r.is_present(): continue
            clx, cly, x, y = r.get_coordinates()
            if r.age >0:
                # Draw robot circles
                # print clx, cly
                if not isnan(clx) and not isnan(cly):
                    if self.draw_robot:
                        # Draw circle
                        cv2.imshow('frame2', cv2.circle(self.frame, (int(clx), int(cly)), ROBOT_DISTANCE, BGR_COMMON['black'], 2, 0))

                        # Draw Names
                        cv2.imshow('frame2', cv2.putText(self.frame, r.name, (int(clx)-15, int(cly)+40), cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))

                    if self.draw_direction:
                        # Draw angle in degrees
                        cv2.imshow('frame2', cv2.putText(self.frame, str(int(r.get_robot_heading())), (int(clx) - 15, int(cly) + 30),
                                                     cv2.FONT_HERSHEY_COMPLEX, 0.45, (100, 150, 200)))

                        # Draw line
                        angle = r.get_robot_heading()
                        new_x = clx + 30 * cos(radians(angle))
                        new_y = cly + 30 * sin(radians(angle))
                        cv2.imshow('frame2', cv2.line(self.frame, (int(clx), int(cly)),
                                                             (int(new_x), int(new_y)), (200, 150, 50), 3, 0))

        if self.draw_ball:
            counter += 1
            if 'x' in self.regular_positions.keys():
                x_ball = self.regular_positions['x']
                y_ball = self.regular_positions['y']

                cv2.imshow('frame2', cv2.circle(self.frame, (int(x_ball), int(y_ball)), 8, (0, 0, 255), 2, 0))
                #cv2.imshow('frame2', cv2.arrowedLine(self.frame, (int(x_ball_prev), int(y_ball_prev)),
                           #(abs(int(x_ball+(10*(x_ball-x_ball_prev)))), abs(int(y_ball+(10*(y_ball-y_ball_prev))))), (0, 255, 0), 3, 10))
                if counter >= 5:
                    x_ball_prev_prev=x_ball_prev
                    y_ball_prev_prev=y_ball_prev
                    x_ball_prev = x_ball
                    y_ball_prev = y_ball

                    counter = 0
                cv2.imshow('frame2', cv2.arrowedLine(self.frame, (int(x_ball_prev_prev), int(y_ball_prev_prev)),
                    (abs(int(x_ball+(5*(x_ball_prev-x_ball_prev_prev)))), abs(int(y_ball+(5*(y_ball_prev-y_ball_prev_prev))))), (0, 255, 0), 3, 10))
                #print r.get_angle()
    
        if self.draw_GUI:
            self.gui.drawGUI()

        #self.model_positions = self.averagePositions(3, self.model_positions)

    def averagePositions(self, frames, positions_in):
        """
        :param frames: number of frames to average
        :param positions_in: positions for the current frame
        :return: averaged positions
        """

        validFrames = self.frameQueue.__len__() + 1

        positions_out = deepcopy(positions_in)
        # Check that the incoming positions have legal values
        for obj in positions_out.items():
            if (positions_out[obj[0]].velocity is None):
                positions_out[obj[0]].velocity = 0
            if positions_out[obj[0]].x is None:
                positions_out[obj[0]].x = 0
            if positions_out[obj[0]].y is None:
                positions_out[obj[0]].y = 0
            positions_out[obj[0]].angle = positions_in[obj[0]].angle

        # Loop over queue
        for positions in self.frameQueue:
            # Loop over each object in the position dictionary
            isFrameValid = True
            for obj in positions.items():
                # Check if the current object's positions have legal values
                if (obj[1].x is None) or (obj[1].y is None) or (obj[1].angle is None) or (obj[1].velocity is None):
                    isFrameValid = False
                else:
                    positions_out[obj[0]].x += obj[1].x
                    positions_out[obj[0]].y += obj[1].y
                    positions_out[obj[0]].velocity += obj[1].velocity

            if not isFrameValid and validFrames > 1:
                #validFrames -= 1
                pass

        # Loop over each object in the position dictionary and average the values
        for obj in positions_out.items():
            positions_out[obj[0]].velocity /= validFrames
            positions_out[obj[0]].x /= validFrames
            positions_out[obj[0]].y /= validFrames


        # If frameQueue is already full then pop the top entry off
        if self.frameQueue.__len__() >= frames:
            self.frameQueue.pop(0)

        # Add our new positions to the end
        self.frameQueue.append(positions_in)

        return positions_out

    def saveCalibrations(self):
        Configuration.write_calibration(self.calibration)
