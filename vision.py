from collections import namedtuple
from multiprocessing import Process, Queue
from threading import Thread

import cv2

from ball_tracker import BallTracker
from config import Configuration
from robot_tracker import RobotTracker
from util import tools


def nothing(x): pass


TEAM_COLORS = {'yellow', 'blue'}
SIDES       = ['left', 'right']
PITCHES     = [0, 1]

PROCESSING_DEBUG = False

Center = namedtuple('Center', 'x y')

class Vision:
    """
    Locate objects on the pitch.
    """

    def __init__(self,
                 pitch,
                 frame_shape,
                 frame_center,
                 calibration,
                 robots,
                 trackers_out,
                 return_circle_contours=False):
        """
        Initialize the vision system.

        Params:
            [int] pitch         pitch number (0 or 1)
            [string] color      color of our robot
            [string] our_side   our side

            [boolean] return_circle_contours - will return circle contours as well as calculated robot locations.
                                               Made for color calibration GUI.
        """
        self.pitch = pitch
        self.frame_center = frame_center

        height, width, channels = frame_shape

        # Find the zone division
        self.zones = self._get_zones(width, height)

        #
        self.return_circle_contours = return_circle_contours

        # Set up trackers
        self.ball_tracker = BallTracker(
           (0, width, 0, height), 0, pitch, calibration)

        self.circle_tracker = RobotTracker(
            ['yellow', 'blue'], ['green', 'pink'], (0, width, 0, height), pitch,
            calibration, robots, return_circle_contours)

        trackers_out.append(self.ball_tracker)
        trackers_out.append(self.circle_tracker)

        


    def _get_zones(self, width, height):
        return [(val[0], val[1], 0, height)
                for val in tools.get_zones(width,
                                           height,
                                           pitch=self.pitch)]

    def perform_locate(self, frame):
        """
        Find objects on the pitch using multiprocessing.

        Returns:
            [5-tuple] Location of the robots and the ball
        """
        # Run trackers as processes
        results = self._run_trackers(frame)

        regular_positions = results[0] if results[0] is not None else dict()
        regular_positions.update(results[1])

        objects = dict()
        if 'x' in regular_positions:
            objects['ball'] = (regular_positions['x'], regular_positions['y'])
        if 'robot_coords' in regular_positions:
            objects['robots'] = regular_positions['robot_coords']

        contours = {
            'circles': regular_positions.get('circles'),
            'ball'   : regular_positions.get('ball_contour')
        }
        return objects, contours


    def _run_trackers(self, frame):
        """
        Run trackers as separate processes

        Params:
            [np.frame] frame        - camera frame to run trackers on

        Returns:
            [5-tuple] positions     - locations of the robots and the ball
        """
        queues = [Queue() for i in range(2)]
        objects = [
                   self.ball_tracker,
                   self.circle_tracker]

        return [self.ball_tracker.find(frame, queues[0]),
        self.circle_tracker.find(frame, queues[1])]

        # Creates separate process for each Tracker from objects array, calling
        # 'find' and passing in the current frame and a fresh queue.

        # processes = [
        #     Thread(target=obj.find, args=(frame, queues[i]))
        #                                     for (i, obj)
        #                                     in enumerate(objects)]
        #
        #
        #
        # # Start processes
        # for process in processes:
        #     process.start()
        #
        # # Find robots and ball, use queue to
        # # avoid deadlock and share resources
        positions = [q.get() for q in queues]

        # Wait for process end
        # for process in processes:
        #     process.join()
        return positions



class Camera(object):
    """
    Camera access wrapper.
    """

    def __init__(self, pitch):
        self.pitch   = pitch
        self.capture = None

        cropping = tools.get_croppings(pitch=pitch)

        # TODO: Find cropping values for each pitch
        self.crop_values = tools.find_extremes(
            cropping['outline'])

        # TODO: Find and pickle radial distortion data for each pitch
        # Parameters used to fix radial distortion
        radial_data = tools.get_radial_data()
        self.nc_matrix = radial_data['new_camera_matrix']
        self.c_matrix = radial_data['camera_matrix']
        self.dist = radial_data['dist']

    def start_capture(self):
        # noinspection PyArgumentList
        self.capture = cv2.VideoCapture(0)

    def stop_capture(self):
        if self.capture:
            self.capture.release()
            self.capture = None

    def get_frame(self):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        # Capture frame-by-frame
        status, frame = self.capture.read()

        frame = self.fix_radial_distortion(frame)
        if status:
            return frame[
                self.crop_values[2]:self.crop_values[3],
                self.crop_values[0]:self.crop_values[1]
            ]

    def fix_radial_distortion(self, frame):
        return cv2.undistort(
            frame, self.c_matrix, self.dist, None, self.nc_matrix)

    def get_adjusted_center(self):
        return 320 - self.crop_values[0], 240 - self.crop_values[2]


