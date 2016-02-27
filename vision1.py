import cv2
import tools
from tracker1 import CircleTracker, BallTracker
from multiprocessing import Process, Queue
from collections import namedtuple
import subprocess
import numpy as np
import time
from colors import BGR_COMMON
from testgui import GUI

def nothing(x): pass

TEAM_COLORS = set(['yellow', 'blue'])
SIDES = ['left', 'right']
PITCHES = [0, 1]

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

        self.v4l_settings()
        #self.GUI = GUI(calibration=calibration, pitch=pitch, launch=self)
        self.frame_center = frame_center

        height, width, channels = frame_shape

        # Find the zone division
        self.zones = zones = self._get_zones(width, height)

        #
        self.return_circle_contours = return_circle_contours

        # Set up trackers
        self.ball_tracker = BallTracker(
           (0, width, 0, height), 0, pitch, calibration)

        self.circle_tracker = CircleTracker(
            ['yellow', 'blue'], ['green', 'pink'], (0, width, 0, height), pitch, calibration)




        # create GUI
        # The first numerical value is the starting point for the vision feed
        cv2.namedWindow('frame2')
        cv2.createTrackbar('bright','frame2',180,255,nothing)
        cv2.createTrackbar('contrast','frame2',120,200,nothing)
        cv2.createTrackbar('color','frame2',80,255,nothing)
        cv2.createTrackbar('hue','frame2',5,30,nothing)
        cv2.createTrackbar('Red Balance','frame2',5,20,nothing)
        cv2.createTrackbar('Blue Balance','frame2',0,20,nothing)


    def v4l_settings(self):
        # it would be nice to reset settings after executing the program..
        video0_old = {}

        # for faraway room
        if self.pitch == 1:
            attributes = ["bright", "contrast", "color", "hue"]
            video0_new = {"bright": 23296, "contrast": 28384, "color": 65408, "hue": 38072}
        #for closest room
        elif self.pitch == 0:
            attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
            video0_new = {"bright": cv2.getTrackbarPos('bright', 'frame2'), "contrast": cv2.getTrackbarPos('contrast','frame2'), 
            "color": cv2.getTrackbarPos('color','frame2'), "hue": cv2.getTrackbarPos('hue', 'frame2'),
            "Red Balance": cv2.getTrackbarPos('Red Balance', 'frame2'), "Blue Balance" : cv2.getTrackbarPos('Blue Balance', 'frame2')}

        # attributes = ["bright", "contrast", "color", "hue"]
        # video0_new = {"bright": 160, "contrast": 110, "color": 100, "hue": 0,"Red Balance": 0, "Blue Balance" : 5}
	unknowns = []

        for attr in attributes:
            output, err = subprocess.Popen(["v4lctl", "show", attr],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if not output.strip():
                print "[WARNING] Unknown video attribute '"+attr+"'"
                unknowns.append(attr)
            else:
                video0_old[attr] = int(output[len(attr)+1:])
                if video0_old[attr] != video0_new[attr]:
                    p = subprocess.Popen(["v4lctl", "setattr", attr, str(video0_new[attr])], stdout=subprocess.PIPE)
                    output, _ = p.communicate()

        # will only output restore file if any value was different.
        # this also prevents from resetting the file on each run
        # to run this bash file, cd to out main dir (where the .sh file is)
        # type "chmod 755 restore_v4lctl_settings.sh"
        # and then "./restore_v4lctl_settings.sh"
        if (video0_old != video0_new):
            f = open('restore_v4lctl_settings.sh','w')
            f.write('#!/bin/sh\n')
            f.write('echo \"restoring v4lctl settings to previous values\"\n')
            for attr in attributes:
                if attr in unknowns: continue
                f.write("v4lctl setattr " + attr + ' ' + str(video0_old[attr]) + "\n")
                f.write('echo \"setting ' + attr +' to ' + str(video0_old[attr]) + '"\n')
            f.write('echo \"v4lctl values restored\"')
            f.close()
    

    def _get_zones(self, width, height):
        return [(val[0], val[1], 0, height)
                for val in tools.get_zones(width,
                                           height,
                                           pitch=self.pitch)]

    def _get_opponent_color(self, our_color):
        return (TEAM_COLORS - set([our_color])).pop()


    def locate1(self, frame):
        """
        Find objects on the pitch using multiprocessing.

        Returns:
            [5-tuple] Location of the robots and the ball
        """
        # Run trackers as processes
        positions = self._run_trackers(frame)

        regular_positions = positions[0] if positions[0] is not None else dict()
        regular_positions.update(positions[1])

        return regular_positions


    # def locate(self, frame):
    #     """
    #     Find objects on the pitch using multiprocessing.
    #
    #     Returns:
    #         [5-tuple] Location of the robots and the ball
    #     """
    #     # Run trackers as processes
    #     positions = self._run_trackers(frame)
    #     # Correct for perspective
    #     positions = self.get_adjusted_positions(positions)
    #
    #     # Wrap list of positions into a dictionary
    #     keys = ['our_defender',
    #             'our_attacker',
    #             'their_defender',
    #             'their_attacker',
    #             'ball']
    #     regular_positions = dict()
    #     for i, key in enumerate(keys):
    #         regular_positions[key] = positions[i]
    #
    #     # Error check we got a frame
    #     height, width, channels = frame.shape if frame is not None \
    #         else (None, None, None)
    #
    #     model_positions = {
    #         'our_attacker': self.to_info(positions[1], height),
    #         'their_attacker': self.to_info(positions[3], height),
    #         'our_defender': self.to_info(positions[0], height),
    #         'their_defender': self.to_info(positions[2], height),
    #         'ball': self.to_info(positions[4], height)
    #     }
    #
    #     return model_positions, regular_positions

    def get_adjusted_point(self, point):
        """
        Given a point on the plane, calculate the
        adjusted point, by taking into account the
        height of the robot, the height of the
        camera and the distance of the point
        from the center of the lens.
        """
        plane_height = 250.0
        # TWEAK
        robot_height = 18.0
        coefficient = robot_height/plane_height

        x = point[0]
        y = point[1]

        dist_x = float(x - self.frame_center[0])
        dist_y = float(y - self.frame_center[1])

        delta_x = dist_x * coefficient
        delta_y = dist_y * coefficient

        return (int(x-delta_x), int(y-delta_y))

    def get_adjusted_positions(self, positions):
        try:
            for robot in range(4):
                # Adjust each corner of the plate
                for i in range(4):
                    x = positions[robot]['box'][i][0]
                    y = positions[robot]['box'][i][1]
                    positions[robot]['box'][i] = self.get_adjusted_point((x, y))

                new_direction = []
                for i in range(2):
                    # Adjust front line
                    x = positions[robot]['front'][i][0]
                    y = positions[robot]['front'][i][1]
                    positions[robot]['front'][i] = self.get_adjusted_point((x, y))

                    # Adjust direction line
                    x = positions[robot]['direction'][i][0]
                    y = positions[robot]['direction'][i][1]
                    adj_point = self.get_adjusted_point((x, y))
                    new_direction.append(adj_point)

                # Change the namedtuples used for storing direction points
                positions[robot]['direction'] = (
                    Center(new_direction[0][0], new_direction[0][1]),
                    Center(new_direction[1][0], new_direction[1][1]))

                # Adjust the center point of the plate
                x = positions[robot]['x']
                y = positions[robot]['y']
                new_point = self.get_adjusted_point((x, y))
                positions[robot]['x'] = new_point[0]
                positions[robot]['y'] = new_point[1]
        except:
            # At least one robot has not been found
            pass

        return positions

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

        
        """
        Creates separate process for each Tracker from objects array, calling
        'find' and passing in the current frame and a fresh queue.
        """
        processes = [
            Process(target=obj.find, args=(frame, queues[i]))
                                            for (i, obj)
                                            in enumerate(objects)]

        # Start processes
        for process in processes:
            process.start()

        # Find robots and ball, use queue to
        # avoid deadlock and share resources
        positions = [q.get() for q in queues]

        # terminate processes
        for process in processes:
            process.join()

        return positions

    def to_info(self, args, height):
        """
        Returns a dictionary with object position information
        """
        x, y, angle, velocity = None, None, None, None
        if args is not None:
            if 'x' in args and 'y' in args:
                x = args['x']
                y = args['y']
                if y is not None:
                    y = height - y

            if 'angle' in args:
                angle = args['angle']

            if 'velocity' in args:
                velocity = args['velocity']

        return {'x': x, 'y': y, 'angle': angle, 'velocity': velocity}




class Camera(object):
    """
    Camera access wrapper.
    """

    def __init__(self, port=0, pitch=0):

        self.port = port
        self.pitch = pitch
        self.capture = None

        # TODO: Calibrate camera for each pitch
        calibration = tools.get_croppings(pitch=pitch)

        # TODO: Find cropping values for each pitch
        self.crop_values = tools.find_extremes(calibration['outline'])

        # TODO: Find and pickle radial distortion data for each pitch
        # Parameters used to fix radial distortion
        radial_data = tools.get_radial_data()
        self.nc_matrix = radial_data['new_camera_matrix']
        self.c_matrix = radial_data['camera_matrix']
        self.dist = radial_data['dist']

    def start_capture(self):
        # noinspection PyArgumentList
        self.capture = cv2.VideoCapture(self.port)

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
            """
            return frame[
                self.crop_values[2]:self.crop_values[3],
                self.crop_values[0]:self.crop_values[1]
            ]
            """
            return frame

    def fix_radial_distortion(self, frame):
        return cv2.undistort(
            frame, self.c_matrix, self.dist, None, self.nc_matrix)

    def get_adjusted_center(self, frame):
        return 320 - self.crop_values[0], 240 - self.crop_values[2]


