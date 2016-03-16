from cv2 import waitKey
from util import tools
from datetime import datetime
from vision_wrapper import VisionWrapper
from util import time_delta_in_ms
from interface import RobotType, Robot
import threading
import numpy as np
from gui import vision_feed
import os

# Dont think we need this

# goals = {
#     'right': np.array([568.0, 232.5]),
#     'left' : np.array([5.5, 226.0])
# }

ROBOT_DESCRIPTIONS = {
    'blue + green'  : {'main_colour': 'blue',   'side_colour': 'green', 'offset_angle': 15, 'type': 'unknown'},
    'yellow + green': {'main_colour': 'yellow', 'side_colour': 'green', 'offset_angle': 0, 'type': 'unknown'},
    'blue + pink'   : {'main_colour': 'blue',   'side_colour': 'pink',  'offset_angle': 0, 'type': 'unknown'},
    'yellow + pink' : {'main_colour': 'yellow', 'side_colour': 'pink',  'offset_angle': 0, 'type': 'unknown'},
}

class VisionLauncher(object):

    """
    Launches the vision wrapper which calibrates the camera based on preset settings, takes care of object tracking
    and can optionally be called to display callibration GUI.
    """
    def __init__(self, pitch, color_settings, team_colour, our_colour, launch_gui=False, pc_name=None):
        """
        :param pitch: [0, 1]                        0 is the one, closer to the door.
        :param color_settings: [0, small, 1, big]   0 or small for pitch color settings with small numbers (previously - pitch 0)
                                                    1 or big - pitch color settings with big numbers (previously - pitch 1)
        :param launch_GUI: boolean                  Set to True if you want to calibrate the colors.
        :param pc_name: String                      Loads camera and color settings from given PC (BUT NOT SAVE TO) file if its naem is given
        :return:
        """

        self.visionwrap = None
        self.vision1 = None
        self.pitch = pitch
        self.color_settings = color_settings
        self._started = False
        self._closed = True
        self._cv = threading.Condition()
        self.launch_gui = launch_gui
        self.pc_name = pc_name
        self.OUR_NAME = team_colour + ' + ' + our_colour
        assert self.OUR_NAME in ROBOT_DESCRIPTIONS

    def launch_vision(self, robots_on_pitch=list()):
        print "[INFO] Configuring vision"
        self.visionwrap = VisionWrapper(self.pitch, self.color_settings,
                                        self.OUR_NAME, ROBOT_DESCRIPTIONS, self.launch_gui,
                                        self.pc_name, robots_on_pitch)

        print "[INFO] Beginning vision loop"
        self.control_loop()

    def get_robots_raw(self):
        listOfRobots = self.visionwrap.get_robots_raw()
        for robot in listOfRobots:
            if robot[0] == self.OUR_NAME:
                robot[4] = RobotType.OURS
                ROBOT_DESCRIPTIONS[robot[0]]['type'] = 'ours'
            elif ROBOT_DESCRIPTIONS[robot[0]]['main_colour'] \
                == ROBOT_DESCRIPTIONS[self.OUR_NAME]['main_colour']:
                robot[4] = RobotType.FRIENDLY
                ROBOT_DESCRIPTIONS[robot[0]]['type'] = 'friendly'
            else:
                robot[4] = RobotType.ENEMY
                ROBOT_DESCRIPTIONS[robot[0]]['type'] = 'enemy'
        return [tuple(r) for r in listOfRobots]

    def get_robot_midpoint(self, robot_name):
        return self.visionwrap.get_robot_position(robot_name)

    def get_side_circle(self, robot_name):
        return self.visionwrap.get_circle_position(robot_name)

    def get_ball_position(self):
        return self.visionwrap.get_ball_position()

    def get_robot_direction(self, robot_name):
        return self.visionwrap.get_robot_direction(robot_name)

    def do_we_have_ball(self, robot_name):
        return self.visionwrap.do_we_have_ball(robot_name)

    def is_ball_in_range(self, robot_name):
        return self.visionwrap.is_ball_in_range(robot_name)

    def is_ball_close(self, robot_name, zone):
        """
        :param robot_name:
        :param zone:        ["left", "right", "bottom"]
        :return:
        """
        return self.visionwrap.is_ball_on_other(robot_name, zone)

    def get_circle_contours(self):
        return self.visionwrap.get_circle_contours()

    def get_goal_positions(self):
        """
        Takes the pitch croppings and estimates the goal corners
        :return: [tuple(x,y),tuple(x,y),tuple(x,y),tuple(x,y)]
        """
        PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        filename = PATH+'/calibrations/croppings.json'
        croppings = tools.get_croppings(filename, self.pitch)['outline']
        if self.pitch == 1:
            return [(croppings[0][0] - 50, int(croppings[3][1]/2) - 60), (croppings[0][0] - 50, int(croppings[3][1]/2) + 50), (croppings[1][0] - 60, int(croppings[2][1]/2) - 50), (croppings[1][0] - 60, int(croppings[2][1]/2 + 60))]
        else:
            return [(croppings[0][0] - 50, int(croppings[3][1]/2) - 60), (croppings[0][0] - 50, int(croppings[3][1]/2) + 50), (croppings[1][0] - 60, int(croppings[2][1]/2) - 70), (croppings[1][0] - 60, int(croppings[2][1]/2 + 40))]

    def get_frame_size(self):
        return self.visionwrap.get_frame_size()

    def wait_for_start(self, timeout=None):
        """
        Sleeps the current thread until the vision system is ready
        or the given timeout has elapsed.
        :param timeout: Timeout in seconds or None.
        :return: True if vision system ready, False if timed-out.
        """
        if not self._started:
            with self._cv:
                start = datetime.now()
                self._cv.wait(timeout)

                # If timed-out, then the time taken >= timeout value
                return timeout is None or time_delta_in_ms(start, datetime.now()) < \
                        int(timeout * 1000)

    def get_previous_ball(self):
        return self.visionwrap.gui.x_ball_prev, self.visionwrap.gui.y_ball_prev

    def get_previous_previous_ball(self):
        return self.visionwrap.gui.x_ball_prev_prev, self.visionwrap.gui.y_ball_prev_prev

    def get_zones(self):
        return tools.get_defense_zones(self.pitch)

    def control_loop(self):
        """
        The main loop for the control system. Runs until 'q' is pressed.

        Takes a frame from the camera; processes it, gets the world state;
        gets the actions for the robots to perform;  passes it to the robot
        controllers before finally updating the GUI.
        """
        keypress = -1
        try:
            self._closed = False
            while keypress != ord('q') and not self._closed:  # the 'q' key
                keypress = waitKey(1) & 0xFF
                self.visionwrap.change_drawing(keypress)

                # update the vision system with the next frame
                self.visionwrap.update()

                # Wait until robot detected
                if not self._started and self.get_robot_midpoint(self.OUR_NAME) is not None \
                    and not np.isnan(self.get_robot_midpoint(self.OUR_NAME)[0]) \
                    and self.get_ball_position() is not None:
                    self._started = True
                    with self._cv:
                        self._cv.notifyAll()
        finally:
            # TODO - close the tk window here?

            print "[VISION] Releasing camera"
            self.visionwrap.camera.stop_capture()

    def get_pitch_dimensions(self):
        from util.tools import get_pitch_size
        return get_pitch_size(self.pitch)

    def close(self):
        self._closed = True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Pitch next to door, [1] Pitch farther from the door")
    parser.add_argument("color_settings", help="pitch room color settings. One of (small, big) or (0, 1)")
    parser.add_argument("team_colour", help="Team colour, blue or yellow")
    parser.add_argument("our_colour", help="Our distinguishing colour, green or pink")
    parser.add_argument("plan", help="Task no. to execute. 'GUI' to launch calibration GUI.")
    parser.add_argument("goal", help="Which goal to target - one of (left, right)")
    parser.add_argument("--override", help="loads color and camera settings from a file with specified computer name. STILL SAVES THE DATA FOR LOCAL MACHINE")

    args = parser.parse_args()

    if args.plan == 'GUI':
        if args.override:
            pc_name = args.override + ".inf.ed.ac.uk"
        else:
            pc_name = None
        vision_launcher = VisionLauncher(int(args.pitch), args.color_settings,args.team_colour, args.our_colour, True, pc_name)

    else:
        # TODO: Need to configure for pitch
        vision_launcher = VisionLauncher(int(args.pitch), args.color_settings,args.team_colour, args.our_colour)

        # Create planner
        """
        planner = Planner(vision_launcher, {'their_goal': goals[args.goal]})

        if args.plan == '1':
            planner.begin_task1()
        elif args.plan == '3':
            planner.begin_task3()
        else:
            raise Exception("Incorrect task number.")
        """

    vision_launcher.launch_vision()
    exit()


