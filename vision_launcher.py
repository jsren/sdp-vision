import threading

import numpy as np
from cv2 import waitKey

from util import tools
from vision_wrapper import VisionWrapper

OUR_NAME = "yellow + pink"

goals = {
    'right': np.array([568.0, 232.5]),
    'left': np.array([5.5, 226.0])
}

ROBOT_DESCRIPTIONS = {
    'blue + green'  : {'main_colour': 'blue', 'side_colour': 'green'},
    'yellow + green': {'main_colour': 'yellow', 'side_colour': 'green'},
    'blue + pink'   : {'main_colour': 'blue', 'side_colour': 'pink'},
    'yellow + pink' : {'main_colour': 'yellow', 'side_colour': 'pink'}
}

assert OUR_NAME in ROBOT_DESCRIPTIONS


class VisionLauncher(object):
    """
    Launches the vision wrapper which calibrates the camera based on preset settings, takes care of object tracking
    and can optionally be called to display callibration GUI.
    """
    def __init__(self, pitch, launch_gui=False):
        """
        :param pitch: [0, 1]            0 is the one, closer to the door.
        :param launch_GUI: boolean      Set to True if you want to calibrate the colors.
        :return:
        """
        self.visionwrap = None
        self.vision1 = None
        self.pitch = pitch
        self._started = False
        self._cv = threading.Condition()
        self._thread = threading.currentThread().getName()
        self.launch_gui = launch_gui

        import signal
        for sig in (signal.SIGABRT, signal.SIGILL,
                    signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
            signal.signal(sig, self._atexit)

    def launch_vision(self):
        print "[INFO] Configuring vision"
        self.visionwrap = VisionWrapper(self.pitch, OUR_NAME, ROBOT_DESCRIPTIONS, self.launch_gui)

        print "[INFO] Beginning vision loop"
        self.control_loop()

    def get_robots_raw(self):
        return self.visionwrap.get_robots_raw()

    def get_robot_midpoint(self, robot_name=OUR_NAME):
        return self.visionwrap.get_robot_position(robot_name)

    def get_side_circle(self, robot_name=OUR_NAME):
        return self.visionwrap.get_circle_position(robot_name)

    def get_ball_position(self):
        return self.visionwrap.get_ball_position()

    def get_robot_direction(self, robot_name=OUR_NAME):
        return self.visionwrap.get_robot_direction(robot_name)

    def do_we_have_ball(self, robot_name=OUR_NAME):
        return self.visionwrap.do_we_have_ball(robot_name)

    def get_circle_contours(self):
        return self.visionwrap.get_circle_contours()

    def wait_for_start(self, timeout=None):
        if not self._started:
            if threading.currentThread().getName() == self._thread:
                raise Exception("You cannot wait for the vision "
                                "to start running on the same thread!")
            else:
                with self._cv:
                    self._cv.wait(timeout)

    def control_loop(self):
        """
        The main loop for the control system. Runs until 'q' is pressed.

        Takes a frame from the camera; processes it, gets the world state;
        gets the actions for the robots to perform;  passes it to the robot
        controllers before finally updating the GUI.
        """
        keypress = -1
        try:
            while keypress != ord('q'):  # the 'q' key
                keypress = waitKey(1) & 0xFF
                self.visionwrap.change_drawing(keypress)

                # update the vision system with the next frame
                self.visionwrap.update()

                #self.visionwrap.vision.v4l_settings()

                if not self.launch_gui:
                    # Wait until robot detected
                    if not self._started and self.get_robot_midpoint() is not None:
                        self._started = True
                        with self._cv:
                            self._cv.notifyAll()
        finally:
            self.visionwrap.camera.stop_capture()
            #print self.visionwrap.do_we_have_ball(OUR_NAME)
            tools.save_colors(self.pitch, self.visionwrap.calibration)

    def _atexit(self, *args):
        try:
            self.visionwrap.camera.stop_capture()
            print "[INFO] Releasing camera"
        except:
            pass

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Pitch next to door, [1] Pitch farther from the door")
    parser.add_argument("plan", help="Task no. to execute. 'GUI' to launch calibration GUI.")
    parser.add_argument("goal", help="Which goal to target - one of (left, right)")

    args = parser.parse_args()

    if args.plan == 'GUI':
        vision_launcher = VisionLauncher(int(args.pitch), True)

    else:
        # TODO: Need to configure for pitch
        vision_launcher = VisionLauncher(int(args.pitch))

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


