
class _RobotType(object):
    UNKNOWN  = 0
    OURS     = 1
    FRIENDLY = 2
    ENEMY    = 4
RobotType = _RobotType()


class Robot(object):
    _position = (None, None)
    _heading  = None
    _type     = RobotType.UNKNOWN
    _has_ball = False
    _name     = None

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
        return self._has_ball



# TODO: Implement me
class VisionInterface(object):

    _launcher = None

    def __init__(self, vision_launcher):
        self._launcher = vision_launcher

    def get_robots(self):
        raise NotImplementedError()

    def wait_for_start(self, timeout=None):
        return self._launcher.wait_for_start(timeout)

    def launch_vision(self):
        raise NotImplementedError()

    def get_ball_position(self):
        return self._launcher.get_ball_position()




