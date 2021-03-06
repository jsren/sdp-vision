""" Interface.py - (c) SDP Team E 2016
    -------------------------------------
    Authors: James Renwick
    Team: SDP Team E
"""
import threading
import operator
import math

class _RobotType(object):
    UNKNOWN  = 0
    OURS     = 1
    FRIENDLY = 2
    ENEMY    = 4
RobotType = _RobotType()


class Robot(object):
    _name     = None
    _position = (None, None)
    _heading  = None
    _type     = RobotType.UNKNOWN

    # Has ball is calculated on an as-needed basis
    _has_ball_delegate = None

    def __init__(self, name, visible, pos, heading, type=RobotType.UNKNOWN,
                 has_ball_func=None, ball_in_range_func=None, ball_in_other_func=None):
        self._name     = name
        self._position = pos
        self._heading  = heading
        self._type     = type
        self._visible  = visible

        self._has_ball_delegate = has_ball_func
        self._ball_in_range_delegate = ball_in_range_func
        self._ball_in_other_delegate = ball_in_other_func

    @property
    def name(self):
        """ Gets the robot designation. Normally the colour pattern. """
        return self._name

    @property
    def position(self):
        """ Gets the robot's mid-point position.
        :return: tuple(x, y).
        """
        return self._position

    @property
    def visible(self):
        """ Gets whether the robot is currently detected. """
        x, y = self.position
        return not (math.isnan(x) or math.isnan(y))

    @property
    def heading(self):
        """ Gets the robot's current heading in degrees. """
        self._heading %= 360
        if self._heading > 180:
            self._heading -= 360
        return self._heading

    @property
    def type(self):
        """ Gets the robot's type: whether our robot, friendly or an enemy.
        :return: `RobotType`
        """
        return self._type

    @property
    def has_ball(self):
        """ Gets whether the robot currently has the ball. """
        if self._has_ball_delegate is not None:
            return self._has_ball_delegate(self.name)
        else:
            return None

    @property
    def ball_in_range(self):
        """
        Returns True if ball is in the grabbing zone
        """
        if self._ball_in_range_delegate is not None:
            return self._ball_in_range_delegate(self.name)
        else:
            return None

    @property
    def ball_in_left(self):
        """
        Returns True if ball is in the left zone
        """
        if self._ball_in_other_delegate is not None:
            return self._ball_in_other_delegate(self.name, "left")
        else:
            return None

    @property
    def ball_in_right(self):
        """
        Returns True if ball is in the right zone
        """
        if self._ball_in_other_delegate is not None:
            return self._ball_in_other_delegate(self.name, "right")
        else:
            return None

    @property
    def ball_in_bottom(self):
        """
        Returns True if ball is in the bottom zone
        """
        if self._ball_in_other_delegate is not None:
            return self._ball_in_other_delegate(self.name, "bottom")
        else:
            return None


# TODO: Test me
class VisionInterface(object):

    _launcher = None

    def __init__(self,  team_color, color_group09, color_group10, pitch, color_settings, gui=True):
        # Create new vision launcher
        from vision_launcher import VisionLauncher as _VisionLauncher
        self._launcher = _VisionLauncher(pitch, color_settings, team_color, color_group09, color_group10, gui)

    def get_robots(self):
        """ Gets the robots currently visible on the pitch.
        :return: A list of `Robot` instances.
        """
        return [ Robot(r[0], r[1], r[2], r[3], r[4], self._launcher.do_we_have_ball, self._launcher.is_ball_in_range,
                       self._launcher.is_ball_close)
            for r in self._launcher.get_robots_raw()]

    def wait_for_start(self, timeout=None):
        """ Blocks the current thread until the vision system is ready.
        :param timeout: Wait timeout in seconds. None for no timeout.
        """
        return self._launcher.wait_for_start(timeout)

    def launch_vision(self):
        """ Launches the vision system. Use `wait_for_start` to sleep the
        current thread until vision system ready.
        :return: The vision system main thread.
        """
        t = threading.Thread(name="Vision Thread",
                             target=self._launcher.launch_vision(["blue + green",
                                                                  "blue + pink",
                                                                  "yellow + green",
                                                                  "yellow + pink"]))
        t.start()
        return t

    def get_frame_size(self):
        return self._launcher.get_frame_size()

    def get_goal_positions(self):
        """ Gets the positions of the back-centre of the goals.
        returns [(left goal left corner), (left goal right corner), (right goal left corner), (right goal right corner)]
        :return: [ tuple(x, y), tuple(x, y), tuple(x,y), tuple(x,y) ]
        """

        left_goal, right_goal =  self._launcher.get_goal_positions()
        left_goal[1] = (left_goal[0][0],left_goal[1][1])
        right_goal[1] = (right_goal[0][0],right_goal[1][1])
        return [tuple(left_goal[0]), left_goal[1], tuple(right_goal[0]), right_goal[1]]

    def get_ball_position(self):
        """ Gets the current ball position.
        :return: tuple(x, y)
        """
        return self._launcher.get_ball_position()

    def get_previous_ball_positions(self):
        return [self._launcher.get_previous_ball(),self._launcher.get_previous_previous_ball()]

    def get_zones(self):
        return self._launcher.get_zones()

    def add_dot(self, location, color):
        return self._launcher.add_dot(location, color)

    def remove_dot(self, location, color=None):
        return self._launcher.remove_dot(location, color)

    def create_gui_variable(self, label, type, initial_value=None):
        return self._launcher.create_gui_variable(label, type, initial_value)

    def update_gui_variable(self, label, value):
        return self._launcher.update_gui_variable(label, value)

    @property
    def pitch_dimensions(self):
        return self._launcher.get_pitch_dimensions()

    def get_centre(self):
        width, height = self.get_frame_size()
        return width / 2, height / 2

    def close(self):
        self._launcher.close()


