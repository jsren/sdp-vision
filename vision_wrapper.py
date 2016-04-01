

import cv2


from gui.vision_feed import GUI
from preprocessing.preprocessing import Preprocessing
from util import RobotInstance
from vision import Vision, Camera
from config import Configuration
from interface import RobotType
# from PIL import Image
from time import time



class VisionWrapper:
    """
    Class that handles vision

    """

    ENEMY_SCALE = 1.
    GROUP9_SCALE = .8
    ALLY_SCALE = 1.

    def __init__(self, pitch, color_settings, our_name, robot_details,
                 enable_gui=False, pc_name=None, robots_on_pitch=list(), goal=None):
        """
        Entry point for the SDP system.

        Params:
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [int or string] color_settings  [0, small, 1, big] - 0 or small for pitch color settings with small numbers (previously - pitch 0)
                                            1 or big - pitch color settings with big numbers (previously - pitch 1)
            [string] colour                 The colour of our teams plates
            [string] our_name               our name
            [int] video_port                port number for the camera

            [boolean] enable_gui              Does not draw the normal image to leave space for GUI.
                                            Also forces the trackers to return circle contour positons in addition to robot details.
            [string] pc_name                Name of the PC to load the files from (BUT NOT SAVE TO). Will default to local machine if not specified.
        """
        pitch = int(pitch)
        assert pitch in [0, 1]

        if goal: assert goal in ["left", "right"]

        self.pitch = pitch
        self.target_goal = goal
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
        self.robots = []

        # Initialize ball states - which robot had the ball previously.
        self.ball_median_size = 5
        self.ball_index = 0
        self.ball_states = [None] * self.ball_median_size

        self.BALL_HOLDING_AREA_SCALE = 0.5

        for r_name in robot_details.keys():
            role = 'ally'
            if robot_details[r_name]['main_colour'] != robot_details[our_name]['main_colour']:
                role = 'enemy'
            elif r_name == our_name:
                role = 'group9'

            print "[WRAPPER] Setting %s to %s." % (r_name, role)
            self.robots.append(RobotInstance(r_name,
                                             robot_details[r_name]['main_colour'],
                                             robot_details[r_name]['side_colour'],
                                             robot_details[r_name]['offset_angle'],
                                             role,
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

        self.side = our_name
        self.frameQueue = []

        self.video = None

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
        """
        :return: Actual ball position or predicted ball position if the robot was near it. Might return None.
        """
        # TODO: call methods here to get robot region if new one will be used.
        if not self.world_objects['ball'][2]:
            r_name, _ = self._mode(self.ball_states)
            if r_name:
                for r in self.robots:
                    if r.name == r_name:
                        x, y = r.predicted_ball_pos
                        self.world_objects['ball'] = (x, y, 2)

        if self.world_objects['ball'][2] and not \
                (self.world_objects['ball'][0] == 42 and self.world_objects['ball'][1] == 42):
            return self.world_objects['ball']
        else:
            return None


    def get_pitch_dimensions(self):
        from util.tools import get_pitch_size
        return get_pitch_size()

    def get_robot_direction(self, robot_name):
        return filter(lambda r: r.name == robot_name, self.robots)[0]


    def do_we_have_ball(self, robot_name):
        return self.is_ball_in_range(robot_name, scale=self.BALL_HOLDING_AREA_SCALE)


    def is_ball_in_range(self, robot_name, scale=1.):
        """
        returns True if ball is in the grabbing zone.
        :param robot_name:  robot name
        :param scale:       Zone can be scaled, to accommodate for different robots
        :return: boolean
        """
        ball = self.get_ball_position()
        if ball and ball[2]:
            for r in self.robots:
                if r.name == robot_name and r.visible:
                    if r.role == 'enemy':
                        if r.is_point_in_grabbing_zone(ball[0], ball[1], role=r.role, scale=self.ENEMY_SCALE, circular=False):
                            return True
                    elif r.role == 'group9':
                        if r.is_point_in_grabbing_zone(ball[0], ball[1], role=r.role, scale=self.GROUP9_SCALE, circular=True):
                            return True
                    else:
                        if r.is_point_in_grabbing_zone(ball[0], ball[1], role=r.role, scale=self.ALLY_SCALE, circular=False):
                            return True
                    break
        return False


    def is_ball_on_other(self, robot_name, zone, scale=1.):
        """
        returns True if ball is in the side or bottom zone.
        :param robot_name:  robot name
        :param zone:        ["left", "right", "bottom"]
        :param scale:       Zone can be scaled, to accommodate for different robots
        :return: boolean
        """
        ball = self.get_ball_position()
        if ball and ball[2]:
            for r in self.robots:
                if r.name == robot_name:
                    if r.is_point_in_other_zone(ball[0], ball[1], zone, role=r.role, scale=scale):
                        return True
                    break
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
            self.gui.draw_ball = not self.gui.draw_ball
        elif key == ord('n'):
            self.gui.draw_contours = not self.gui.draw_contours
        # THIS WAS CRASHING EVERYTHING
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

    def get_frame_size(self):
        height, width, channels = self.frame.shape
        return width, height

    def get_latency_seconds(self):
        return self.delta_t

    def _mode(self, array):
        """
        :param array:   some array
        :return: m, c   the first mode found and the number of occurences
        """
        m = max(array, key = array.count)
        return m, array.count(m)


    def start_video(self, title):
        if self.video is not None:
            try:
                self.video.release()
            except Exception, e:
                print "[WARNING] Error releasing previous video:", e
        self.video = cv2.VideoWriter('recordings/' + "test" + '.mpeg', -1, int(self.camera.capture.get(cv2.CAP_PROP_FPS)),
                                     (int(self.camera.capture.get(3)), int(self.camera.capture.get(4))))

    def end_video(self):
        try:
            self.video.release()
        except Exception, e:
            print "[WARNING] Error releasing previous video:", e
        finally:
            self.video = None

    def update(self):
        """ Processes the current frame. """
        self.frame = self.camera.get_frame()

        # Apply preprocessing methods toggled in the UI
        self.preprocessed = self.preprocessing.run(self.frame, self.preprocessing.options)
        self.frame = self.preprocessed['frame']

        if 'background_sub' in self.preprocessed and self.enable_gui:
            cv2.imshow('bg sub', self.preprocessed['background_sub'])

        # Find object positions
        self.world_objects, self.world_contours = self.vision.perform_locate(self.frame)

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
                        # Add new ball state if robot has the ball.
                        ball = self.get_ball_position()
                        if ball and ball[2] and robot.is_point_in_grabbing_zone(ball[0], ball[1]):
                            self.ball_states[self.ball_index] = robot.name
                        break
            self.ball_index = (self.ball_index + 1) % self.ball_median_size

        # Recalculate the latency time
        t = time()
        self.delta_t = t - self.t0
        self.t0 = t

        video_frame = self.frame

        # Perform GUI update
        if self.enable_gui:
            video_frame = self.gui.update(self)

        # Now write frame to video, if enabled
        if self.video is not None:
            self.video.write(video_frame)





