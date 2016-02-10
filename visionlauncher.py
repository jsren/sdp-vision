import vision.tools as tools
from cv2 import waitKey
import warnings
import time
from visionwrapper import VisionWrapper
# from Control.dict_control import Controller
# from Utility.CommandDict import CommandDict
import traceback
import sys

OUR_NAME = "Team E"

ROBOT_DESCRIPTIONS = {
    'blue + green': {'main_colour':'blue', 'side_colour':'green'},
    #'yellow + green': {'main_colour':'yellow', 'side_colour':'green'},
    'blue + pink': {'main_colour':'blue', 'side_colour':'pink'},
    'yellow + pink': {'main_colour':'yellow', 'side_colour':'pink'}
}

class VisionLauncher(object):

    def __init__(self, pitch):
        self.visionwrap = None
        self.pitch = pitch

    def launch_vision(self):
        self.visionwrap = VisionWrapper(self.pitch, OUR_NAME, ROBOT_DESCRIPTIONS)

        self.control_loop()


    def get_robot_midpoint(self, robot_name=OUR_NAME):
        return self.visionwrap.get_robot_position(robot_name)

    def get_side_circle(self, robot_name=OUR_NAME):
        return self.visionwrap.get_circle_position(robot_name)


    def control_loop(self):
        """
        The main loop for the control system. Runs until 'q' is pressed.

        Takes a frame from the camera; processes it, gets the world state;
        gets the actions for the robots to perform;  passes it to the robot
        controllers before finally updating the GUI.
        """
        counter = 1L
        timer = time.clock()
        try:
            key = 255
            while waitKey(1) & 0xFF != ord('q'):  # the 'q' key

                # update the vision system with the next frame
                self.visionwrap.update()
                pre_options = self.visionwrap.preprocessing.options

                # Find appropriate action
                # command = self.planner.update(self.vision.model_positions)
                # self.controller.update(command)

                fps = float(counter) / (time.clock() - timer)

                # Draw vision content and actions

                counter += 1

        except Exception as e:
            print(e.message)
            traceback.print_exc(file=sys.stdout)
        finally:
            self.visionwrap.camera.stop_capture()
            tools.save_colors(self.pitch, self.visionwrap.calibration)


import numpy as np
goals = {
    'right': np.array([568.0, 232.5]),
    'left': np.array([5.5, 226.0])
}

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
    vision_launcher.launch_vision()

    # Launch planner
    planner = Planner(vision_launcher, {'their_goal': goals[args.goal]})

    if args.plan == 1:
        planner.begin_task1()
    elif args.plan == 3:
        planner.begin_task3()
    else:
        class StupidTitException(Exception):
            def __init__(self): super("Incorrect task, you insufferable douche canoe.")
        raise StupidTitException()





