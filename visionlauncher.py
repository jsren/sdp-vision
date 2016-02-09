from visionwrapper import VisionWrapper

OUR_NAME = "Team E"

ROBOT_DESCRIPTIONS = {
    'Team E': {'main_colour':'blue', 'side_colour':'green'},
    'Team 0': {'main_colour':'yellow', 'side_colour':'green'},
    'Team 1': {'main_colour':'blue', 'side_colour':'pink'},
    'Team 2': {'main_colour':'yellow', 'side_colour':'pink'}
}

class VisionLauncher(object):

    def __init__(self):
        self.visionwrap = None

    def launch_vision(self,pitch):
        self.visionwrap = VisionWrapper(pitch, OUR_NAME, ROBOT_DESCRIPTIONS)


    def get_robot_midpoint(self, robot_name=OUR_NAME):
        return self.visionwrap.get_robot_position(robot_name)

    def get_side_circle(self, robot_name=OUR_NAME):
        return self.visionwrap.get_circle_position(robot_name=OUR_NAME)




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Pitch next to door, [1] Pitch farther from the door")
    parser.add_argument("plan", help="NOT USED AT THE MOMENT - input for the planner")

    args = parser.parse_args()

    vision_launcher = VisionLauncher()
    vision_launcher.launch_vision(pitch=int(args.pitch))
