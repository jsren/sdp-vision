import threading
import vision.tools as tools
import numpy as np

from cv2 import waitKey
from visionwrapper import VisionWrapper


OUR_NAME = "Team E"

goals = {
    'right': np.array([568.0, 232.5]),
    'left' : np.array([5.5, 226.0])
}

ROBOT_DESCRIPTIONS = {
    'blue + green': {'main_colour':'blue', 'side_colour':'green'},
    'yellow + green': {'main_colour':'yellow', 'side_colour':'green'},
    'blue + pink': {'main_colour':'blue', 'side_colour':'pink'},
    'yellow + pink': {'main_colour':'yellow', 'side_colour':'pink'}
}

class StupidTitException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class VisionLauncher(object):
    def __init__(self, pitch):
        self.visionwrap = None
        self.pitch      = pitch
        self._started   = False
        self._cv        = threading.Condition()
        self._thread    = threading.currentThread().getName()

        import signal
        for sig in (signal.SIGABRT, signal.SIGILL,
                    signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
            signal.signal(sig, self._atexit)


    def launch_vision(self):
        print "[INFO] Configuring vision"
        self.visionwrap = VisionWrapper(self.pitch, OUR_NAME, ROBOT_DESCRIPTIONS)
        print "[INFO] Beginning vision loop"
        self.control_loop()

    def get_robot_midpoint(self, robot_name=OUR_NAME):
        return self.visionwrap.get_robot_position(robot_name)

    def get_side_circle(self, robot_name=OUR_NAME):
        return self.visionwrap.get_circle_position(robot_name)

    def wait_for_start(self, timeout=None):
        if not self._started:
            if threading.currentThread().getName() == self._thread:
                raise StupidTitException("You cannot wait for the vision "
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
        try:
            while waitKey(1) & 0xFF != ord('q'):  # the 'q' key
                # update the vision system with the next frame
                self.visionwrap.update()

                if not self._started:
                    self._started = True
                    with self._cv:
                        self._cv.notifyAll()
        finally:
            self.visionwrap.camera.stop_capture()
            tools.save_colors(self.pitch, self.visionwrap.calibration)

    def _atexit(self, *args):
        try:
            self.visionwrap.camera.stop_capture()
            print "[INFO] Releasing camera"
        except:
            pass

if __name__ == '__main__':
    import argparse
    from planner import Planner

    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Pitch next to door, [1] Pitch farther from the door")
    parser.add_argument("plan", help="Task no. to execute.")
    parser.add_argument("goal", help="Which goal to target - one of (left, right)")

    args = parser.parse_args()

    # TODO: Need to configure for pitch
    vision_launcher = VisionLauncher(int(args.pitch))

    # Create planner
    planner = Planner(vision_launcher, {'their_goal': goals[args.goal]})

    if args.plan == '1':
        planner.begin_task1()
    elif args.plan == '3':
        planner.begin_task3()
    else:
        raise StupidTitException("Incorrect task number.")

    vision_launcher.launch_vision()


