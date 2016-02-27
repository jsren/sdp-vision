#!/usr/bin/env python

import sys
from threading import Thread
from communication import Communication
from terminal_display import TerminalDisplay
from vision_launcher import VisionLauncher
from planner_group9 import Planner, MessageHandler, UserInputHandler


class Launcher:
    def __init__(self, usb_port_number, pitch_number):
        world_state_object = None  # TODO World state object here - pitch?
        message_handler = MessageHandler(world_state_object)
        self.com = Communication(message_handler, usb_port_number)
        user_input_handler = UserInputHandler(world_state_object)
        self.display = TerminalDisplay(user_input_handler)

        self.vision = VisionLauncher(pitch_number)
        self.vision_thread = Thread(target=self.vision)

        self.planner = Planner(world_state_object, self.com, self.vision)
        self.planning_thread = Thread(target=self.planner.launch)

    def launch(self):
        print("initialising vision...")
        self.vision_thread.start()
        self.vision.wait_for_start()
        self.planning_thread.start()
        self.display.run()
        self.close()

    def vision(self):
        self.vision.launch_vision()

    def close(self):
        self.display.close()
        self.com.close()


def main(usb_port_number, pitch_number):
    launcher = Launcher(usb_port_number, pitch_number)
    try:
        launcher.launch()
    except KeyboardInterrupt:
        # if the user ctrl-C's or if anything else goes wrong, exit cleanly
        launcher.close()
    except Exception as e:
        launcher.close()
        raise e

if __name__ == '__main__':
    try:
        usb_port_number = sys.argv[1]
    except IndexError:
        usb_port_number = 0

    try:
        pitch_number = sys.argv[1]
    except IndexError:
        pitch_number = 0
    main(usb_port_number, pitch_number)
