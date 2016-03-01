

import cv2


from gui.vision_feed import GUI
from preprocessing.preprocessing import Preprocessing
from util import RobotInstance
from vision import Vision, Camera
from config import Configuration



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

        # Set up camera for frames
        self.camera = Camera(pitch)
        self.camera.start_capture()
        self.frame = self.camera.get_frame()
        center_point = self.camera.get_adjusted_center()

        # Set up vision
        self.trackers = list()

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

        if self.enable_gui:
            self.gui = GUI(self.pitch, self.color_settings, self.calibration, self)

            from threading import Thread
            from gui.common import MainWindow
            from gui.status_control import StatusUI
            from gui.main import MainUI

            self.status_window = None

            def create_windows():
                self.main_window = MainUI(self)
                self.status_window = StatusUI()
                return [
                    self.main_window,
                    self.status_window
                ]

            Thread(name="Tkinter UI", target=MainWindow.create_and_show,
                   args=[create_windows]).start()


        # Set up preprocessing and postprocessing
        # self.postprocessing = Postprocessing()
        self.preprocessing = Preprocessing()

        self.side = our_side
        self.frameQueue = []


    def end(self):
        self.gui.commit_settings()

    def saveCalibrations(self):
        Configuration.write_calibration(self.calibration)

    def get_robots_raw(self):
        # Filter robots that have no position
        return [(r.name, r.position, r.heading)
                for r in self.robots if list(r.x)]

    def get_robot_position(self, robot_name):
        return filter(lambda r: r.name == robot_name, self.robots)[0].position


    def get_circle_position(self, robot_name):
        for r in self.robots:
            if r.name == robot_name:
                return r.side_x, r.side_y

    def get_ball_position(self):
        return self.world_objects.get('ball')

    def get_robot_direction(self, robot_name):
        return filter(lambda r: r.name == robot_name, self.robots)[0]

    def do_we_have_ball(self, robot_name):
        if 'ball' not in self.world_objects: return None

        for r in self.robots:
            if r.name == robot_name:
                ball_x, ball_y = self.world_objects['ball']
                robot_x, robot_y = r.position
                heading = r.heading

                assert heading <= 360

                if heading < 90:
                    return robot_x-10 < ball_x < robot_x+30 and robot_y-10 < ball_y < robot_y+30
                elif heading >= 90 and heading < 180:
                    return robot_x-30 < ball_x < robot_x+10 and robot_y-10 < ball_y < robot_y+30
                elif heading >= 180 and heading < 270:
                    return robot_x-30 < ball_x < robot_x+10 and robot_y-30 < ball_y < robot_y+10
                else:
                    return robot_x-10 < ball_x < robot_x+30 and robot_y-30 < ball_y < robot_y+10


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
        elif key == ord('j'):
            self.gui.draw_robot = not self.gui.draw_robot
        elif key == ord('i'):
            self.gui.draw_direction = not self.gui.draw_direction


    def get_circle_contours(self):
        """
        Careful! Does not return x and y values. Call minimum bounding circles if proper circle locations are required.
        Or look at dem fish http://docs.opencv.org/2.4/doc/tutorials/imgproc/shapedescriptors/find_contours/find_contours.html
        :return: [Contours]
        """
        return self.world_objects.get('circles')


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
            for r_data in self.world_objects['robots']:
                for robot in self.robots:
                    # Only update robots we've set as being present
                    if not robot.present: continue

                    if robot.update(r_data['clx'], r_data['cly'],
                                    r_data['main_color'], r_data['side_color'],
                                    r_data['x'], r_data['y']):
                        break

        # Perform GUI update
        if self.enable_gui:
            self.gui.update(self)

            if self.status_window:
                self.status_window.ball_status_var.value = \
                    'ball' in self.world_objects
