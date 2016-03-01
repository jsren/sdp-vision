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

    def __init__(self, name, pos, heading, has_ball_func=None,
                 type=RobotType.UNKNOWN):
        self._name     = name
        self._position = pos
        self._heading  = heading
        self._type     = type

        self._has_ball_delegate = has_ball_func

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
    def heading(self):
        """ Gets the robot's current heading in degrees. """
        angle = self.heading
        while -180 >= angle or angle > 180:
            if -180 >= angle:
                angle += 360
            else:
                angle -= 360
        self.heading = angle
        return self.heading

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



# TODO: Test me
class VisionInterface(object):

    _launcher = None

    def __init__(self, pitch, gui=True):
        # Create new vision launcher
        from vision_launcher import VisionLauncher \
            as _VisionLauncher
        self._launcher = _VisionLauncher(pitch, gui)

    def get_robots(self):
        """ Gets the robots currently visible on the pitch.
        :return: A list of `Robot` instances.
        """
        return [ Robot(r[0], r[1], r[2], self._launcher.do_we_have_ball)
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
        :return: [ tuple(x, y), tuple(x, y) ]
        """
        return self._launcher.get_goal_positions()

    def get_ball_position(self):
        """ Gets the current ball position.
        :return: tuple(x, y)
        """
        return self._launcher.get_ball_position()


