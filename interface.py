""" Interface.py - (c) SDP Team E 2016
    -------------------------------------
    Authors: James Renwick
    Team: SDP Team E
"""
import threading

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
        return self._visible

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


    def ball_in_other(self, zone):
        """
        :param zone:    ["left", "right", "bottom"]
        Returns True if ball is in the other zone
        """
        if self._ball_in_other_delegate is not None:
            return self._ball_in_other_delegate(self.name, zone)
        else:
            return None


# TODO: Test me
class VisionInterface(object):

    _launcher = None

    def __init__(self,  team_colour, our_colour, pitch, color_settings, gui=True):
        # Create new vision launcher
        from vision_launcher import VisionLauncher \
            as _VisionLauncher
        self._launcher = _VisionLauncher(pitch, color_settings, team_colour, our_colour, gui)

    def get_robots(self):
        """ Gets the robots currently visible on the pitch.
        :return: A list of `Robot` instances.
        """
        return [ Robot(r[0], r[1], r[2], r[3], r[4], self._launcher.do_we_have_ball, self._launcher.is_ball_in_range,
                       self._launcher.is_ball_close)
            for r in self._launcher.get_robots_raw() ]

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
                             target=self._launcher.launch_vision)
        t.start()
        return t

    def get_goal_positions(self):
        """ Gets the positions of the back-centre of the goals.
        returns [(left goal left corner), (left goal right corner), (right goal left corner), (right goal right corner)]
        :return: [ tuple(x, y), tuple(x, y), tuple(x,y), tuple(x,y) ]
        """
        return self._launcher.get_goal_positions()

    def get_ball_position(self):
        """ Gets the current ball position.
        :return: tuple(x, y)
        """
        return self._launcher.get_ball_position()

    @property
    def pitch_dimensions(self):
        return self._launcher.get_pitch_dimensions()

    def close(self):
        self._launcher.close()


