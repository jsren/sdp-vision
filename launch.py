# from planning.Planner import Planner
import vision.tools as tools
from cv2 import waitKey
import cv2
import warnings
import time
from gui import GUI
from visionwrapper import VisionWrapper
# from Control.dict_control import Controller
# from Utility.CommandDict import CommandDict
import traceback
import sys

warnings.filterwarnings("ignore", category=DeprecationWarning)

class Main:


    """
    Primary source of robot control. Ties vision and planning together.
    """
    def __init__(self, pitch, color, our_side, video_port=0, comm_port='/dev/ttyACM0', quick=False, is_attacker=False):
        """
        Entry point for the SDP system.

        Params:
            [int] video_port                port number for the camera
            [string] comm_port              port number for the arduino
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] our_side               the side we're on - 'left' or 'right'
        # """
        '''
        self.controller = Controller(comm_port)

        if not quick:
            print("Waiting 10 seconds for serial to initialise")
            time.sleep(10)

        # Kick once to ensure we are in the correct position
        self.controller.update(CommandDict.kick())
        '''
        self.pitch = pitch


        # Set up the vision system.
        self.vision = VisionWrapper(pitch, color, our_side, video_port)


        # Set up the planner
        # self.planner = Planner(our_side, pitch, attacker=is_attacker)


        # Set up GUI
        self.GUI = GUI(calibration=self.vision.calibration, pitch=pitch, launch=self)

        '''
        # TODO: comment or remove this later
        while True:
            self.vision.update()  # get the new frame
            frame0 = self.vision.frame  # use that new frame

            # Display the resulting frame
            cv2.imshow('frame', frame0)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.vision.camera.stop_capture()
        cv2.destroyAllWindows()
        '''


        self.color = color
        self.side = our_side

        self.control_loop()


     
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
            while key != ord('q'):  # the 'q' key

                # update the vision system with the next frame
                self.vision.update()
                pre_options = self.vision.preprocessing.options

                # Find appropriate action
                # command = self.planner.update(self.vision.model_positions)
                # self.controller.update(command)

                # Information about states
                regular_positions = self.vision.regular_positions
                model_positions = self.vision.model_positions

                # defenderState = (str(self.planner.current_plan), "0")

                # Use 'y', 'b', 'r' to change color.
                key = waitKey(delay=2) & 0xFF  # Returns 255 if no keypress detected
                if key == 'm':
                    print "detection level: launch.py"
                gui_actions = []
                fps = float(counter) / (time.clock() - timer)

                # Draw vision content and actions
                
                self.GUI.draw(
                    self.vision.frame, model_positions, gui_actions, regular_positions, fps, None,
                    defenderState, None, None, False,
                    our_color=self.color, our_side=self.side, key=key, preprocess=pre_options)
                

                exit0 = self.GUI.draw(
                    self.vision.frame, None, gui_actions, regular_positions, fps, None,
                    "current defender state", None, None, False,
                    our_color=self.color, our_side=self.side, key=key, preprocess=pre_options,
                    camera=self.vision.camera)
                
                counter += 1

                if exit0:
                    break




                '''
                # TODO: my code here, so remove it afterwards. --Linas
                frame0 = self.vision.frame  # use that new frame
                # Display the resulting frame
                cv2.imshow('frame', frame0)
                '''




        except Exception as e:
            print(e.message)
            traceback.print_exc(file=sys.stdout)
        finally:
            self.vision.camera.stop_capture()
            tools.save_colors(self.pitch, self.vision.calibration)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    parser.add_argument("comms", help="""The serial port that the RF stick
                        is using (Usually /dev/ttyACMx)""")
    parser.add_argument("role", help="Role of robot - 'attack' or 'defend'")
    parser.add_argument("-q", "--quick", help="Quick mode - skips wait for serial",
                        action="store_true")
    args = parser.parse_args()
    if args.role == "attack" or args.role == "attacker":
        is_attacker = True
    elif args.role == "defend" or args.role == "defender":
        is_attacker = False
    else:
        print "Role must be 'attack' or 'defend'"
        sys.exit()
    print args.pitch
    c = Main(pitch=int(args.pitch), color=args.color, our_side=args.side, comm_port=args.comms,
             quick=args.quick, is_attacker=is_attacker)
