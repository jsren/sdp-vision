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
    'Team E': {'main_colour':'blue', 'side_colour':'green'},
    'Team 0': {'main_colour':'yellow', 'side_colour':'green'},
    'Team 1': {'main_colour':'blue', 'side_colour':'pink'},
    'Team 2': {'main_colour':'yellow', 'side_colour':'pink'}
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
        return self.visionwrap.get_circle_position(robot_name=robot_name)


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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Pitch next to door, [1] Pitch farther from the door")
    parser.add_argument("plan", help="NOT USED AT THE MOMENT - input for the planner")

    args = parser.parse_args()

    vision_launcher = VisionLauncher(0)#int(args.pitch))
    vision_launcher.launch_vision()
