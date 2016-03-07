

import cv2


from gui.vision_feed import GUI
from preprocessing.preprocessing import Preprocessing
from util import RobotInstance
from vision import Vision, Camera
from config import Configuration
from interface import RobotType
from time import time


class VisionWrapper:
    """
    Class that handles vision

    """
    def __init__(self, pitch, color_settings, our_side, robot_details,
                 enable_gui=False, pc_name=None, robots_on_pitch=list()):
        """
        Entry point for the SDP system.

        Params:
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [int or string] color_settings  [0, small, 1, big] - 0 or small for pitch color settings with small numbers (previously - pitch 0)
                                            1 or big - pitch color settings with big numbers (previously - pitch 1)
            [string] colour                 The colour of our teams plates
            [string] our_side               the side we're on - 'left' or 'right'
            [int] video_port                port number for the camera

            [boolean] enable_gui              Does not draw the normal image to leave space for GUI.
                                            Also forces the trackers to return circle contour positons in addition to robot details.
            [string] pc_name                Name of the PC to load the files from (BUT NOT SAVE TO). Will default to local machine if not specified.
        """
        pitch = int(pitch)
        assert pitch in [0, 1]

        self.pitch = pitch
        self.color_settings = color_settings

        self.calibration = Configuration.read_calibration(
            pc_name, create_if_missing=True)

        self.video_settings = Configuration.read_video_config(
            pc_name, create_if_missing=True)

        # Set up camera for frames
        self.camera = Camera(pitch)
        self.camera.start_capture()
        self.frame = self.camera.get_frame()
        center_point = self.camera.get_adjusted_center()

        # Set up vision
        self.trackers = list()

        self.world_objects = dict()

        # Get machine-specific calibration

        self.enable_gui = enable_gui
        self.gui = None

        # Initialize robots
        self.ball   = []
        self.robots = []

        for r_name in robot_details.keys():
            self.robots.append(RobotInstance(r_name,
                                             robot_details[r_name]['main_colour'],
                                             robot_details[r_name]['side_colour'],
                                             robot_details[r_name]['offset_angle'],
                                             r_name in robots_on_pitch))

        # Draw various things on the image
        self.draw_direction = True
        self.draw_robot     = True
        self.draw_contours  = True
        self.draw_ball      = True

        self.vision = Vision(
            pitch=pitch, frame_shape=self.frame.shape,
            frame_center=center_point, calibration=self.calibration,
            robots=self.robots,
            return_circle_contours=enable_gui, trackers_out=self.trackers)

        # Used for latency calculations
        self.t0 = time()
        self.delta_t = 0


        if self.enable_gui:
            self.gui = GUI(self.pitch, self.color_settings, self.calibration, self)

            from threading import Thread
            from gui.common import MainWindow
            from gui.status_control import StatusUI
            from gui.main import MainUI

            self.status_window = None

            def create_windows():
                self.main_window = MainUI(self)
                return [ self.main_window ]

            Thread(name="Tkinter UI", target=MainWindow.create_and_show,
                   args=[create_windows]).start()



        # Set up preprocessing and postprocessing
        # self.postprocessing = Postprocessing()
        self.preprocessing = Preprocessing()

        self.side = our_side
        self.frameQueue = []


    def get_robots_raw(self):
        # Filter robots that have no position
        return [[r.name, r.visible, r.position, r.heading, RobotType.UNKNOWN]
                for r in self.robots]

    def get_robot_position(self, robot_name):
        return filter(lambda r: r.name == robot_name, self.robots)[0].position

    def get_robot_headings(self):
        headings = dict()
        for r in self.robots:
            headings[r.name] = r.heading
        return headings


    def get_circle_position(self, robot_name):
        for r in self.robots:
            if r.name == robot_name:
                return r.side_x, r.side_y

    def get_all_robots(self):
        robots = dict()
        for r in self.robots:
            robots[r.name] = self.get_robot_position(r.name)
        return robots

    def get_ball_position(self):
        return self.world_objects.get('ball')

    def get_robot_direction(self, robot_name):
        return filter(lambda r: r.name == robot_name, self.robots)[0]

    def do_we_have_ball(self, robot_name):
        if 'ball' not in self.world_objects:
            return None

        for r in self.robots:
            if r.name == robot_name:
                ball_x, ball_y = self.world_objects['ball']
                robot_x, robot_y = r.position
                heading = r.heading

                # TODO fix these values

                width = 10
                depth = 10

                if heading < 90:
                    return robot_x-width < ball_x < robot_x+depth and robot_y-width < ball_y < robot_y+depth
                elif 90 <= heading < 180:
                    return robot_x-depth < ball_x < robot_x+width and robot_y-width < ball_y < robot_y+depth
                elif 180 <= heading < 270:
                    return robot_x-depth < ball_x < robot_x+width and robot_y-30 < ball_y < robot_y+width
                else:
                    return robot_x-width < ball_x < robot_x+depth and robot_y-30 < ball_y < robot_y+width

    def is_ball_in_range(self, robot_name):
        if 'ball' not in self.world_objects:
            return None

        for r in self.robots:
            if r.name == robot_name:
                ball_x, ball_y = self.world_objects['ball']
                robot_x, robot_y = r.position
                heading = r.heading

                # TODO confirm these values (display on vision feed)

                width = 10
                depth = 30

                if heading < 90:
                    return robot_x-width < ball_x < robot_x+depth and robot_y-width < ball_y < robot_y+depth
                elif 90 <= heading < 180:
                    return robot_x-depth < ball_x < robot_x+width and robot_y-width < ball_y < robot_y+depth
                elif 180 <= heading < 270:
                    return robot_x-depth < ball_x < robot_x+width and robot_y-30 < ball_y < robot_y+width
                else:
                    return robot_x-width < ball_x < robot_x+depth and robot_y-30 < ball_y < robot_y+width


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
            self.gui.draw_ball = not self.gui.draw_ball
        elif key == ord('n'):
            self.gui.draw_contours = not self.gui.draw_contours
        # TODO: this was crashing everything
        # elif key == ord('j'):
        #     self.gui.draw_robot = not self.gui.draw_robot
        elif key == ord('i'):
            self.gui.draw_direction = not self.gui.draw_direction


    def get_circle_contours(self):
        """
        Careful! Does not return x and y values. Call minimum bounding circles if proper circle locations are required.
        Or look at dem fish http://docs.opencv.org/2.4/doc/tutorials/imgproc/shapedescriptors/find_contours/find_contours.html
        :return: [Contours]
        """
        return self.world_objects.get('circles')

    def get_latency_seconds(self):
        return self.delta_t

    def update(self):
        """ Processes the current frame. """
        self.frame = self.camera.get_frame()

        # Apply preprocessing methods toggled in the UI
        self.preprocessed = self.preprocessing.run(self.frame, self.preprocessing.options)
        self.frame = self.preprocessed['frame']

        if 'background_sub' in self.preprocessed and self.enable_gui:
            cv2.imshow('bg sub', self.preprocessed['background_sub'])

        # Find object positions
        # model_positions have their y coordinate inverted
        # TODO: is this still the case?
        self.world_objects, self.world_contours = \
            self.vision.perform_locate(self.frame)

        # Updates the robot coordinates
        if 'robots' in self.world_objects:
            for topplate in self.world_objects['robots']:
                for robot in self.robots:
                    # Only update robots we've set as being present
                    if not robot.present: continue

                    # Adds the side marker coordinates
                    other_circle_coords = []
                    for marker in topplate.markers[1:]:
                        other_circle_coords.append((marker['pos'][0], marker['pos'][1]))

                    if robot.update(topplate.naive_midpoint[0], topplate.naive_midpoint[1],
                                    topplate.primary_color, topplate.secondary_color,
                                    topplate.markers[0]['pos'][0] if any(topplate.markers)
                                        else None,
                                    topplate.markers[0]['pos'][1] if any(topplate.markers)
                                        else None,
                                    other_circle_coords
                                    ):
                        break

        # Recalculate the latency time
        t = time()
        self.delta_t = t - self.t0
        self.t0 = t

        # Perform GUI update
        if self.enable_gui:
            self.gui.update(self)



