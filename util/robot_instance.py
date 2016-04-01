from math import degrees, atan2
import numpy as np
from math import radians, cos, sin

# Angle offset of marker on top plate.
# Not sure if clockwise or anti-clockwise.
marker_angle_offset = 34.509

MEDIAN_SWITCH_ANGLE_THRESHOLD = 25
MEDIAN_SWITCH_DISTANCE_THRESHOLD = 30

MIDPOINT_TO_BALL_ZONE = 10
BALL_ZONE_HEIGHT = 30
BALL_ZONE_WIDTH = 25
SIDE_ZONE_HEIGHT = 25
SIDE_ZONE_WIDTH = 40
BACK_ZONE_HEIGHT = 25
BACK_ZONE_WIDTH = 40
ROBOT_WIDTH = 90
ROBOT_HEIGHT = 90


class RobotInstance(object):

    def __init__(self, name, m_color, s_color, offset_angle, role, present=False):
        """
        DO NOT USE OTHER CIRCLE COORDINATES FOR CALCULATIONS - THEY'RE NOT IN A QUEUE
        """
        self.queue_size = 5
        self.x = list()
        self.y = list()
        self.main_color = m_color
        self.side_color = s_color
        self.offset_angle = offset_angle  # individual error offset
        self.role = role
        self.name = name
        self.side_x = list()
        self.side_y = list()
        self.age = 0
        self.angle = list()
        self.other_coords = list()
        self._latest_values = list()

        # Used for median selector
        self._latest_angle = 0
        self._latest_coords = (None, None)

        self._visible = False
        self._present = bool(present)

    def update(self, x, y, m_color, s_color, side_x, side_y, other_coords):
        if self.main_color == m_color and self.side_color == s_color:
            # Elements are inserted into the beginning of the queue
            self.x.insert(0, x); self.x = self.x[:self.queue_size]
            self.y.insert(0, y); self.y = self.y[:self.queue_size]
            self.side_y.insert(0, side_y); self.side_y = self.side_y[:self.queue_size]
            self.side_x.insert(0, side_x); self.side_x = self.side_x[:self.queue_size]
            self.angle.insert(0, self._get_angle()); self.angle = self.angle[:self.queue_size]
            self.other_coords = other_coords
            self._latest_values = other_coords + [(x, y), (side_x, side_y)]

            # Set last found angle and coordinates for median selector.
            if self._latest_angle == 0:
                self._latest_angle = self._get_angle()
                self._latest_coords = (x, y)

            self._visible = True
            self.age = 30
            return True
        else:
            self.age -= 1
            if self.age == 0:
                self.reset()
            return False

    @property
    def present(self):
        return self._present

    @present.setter
    def present(self, value):
        self._present = bool(value)

    @property
    def visible(self):
        return self._present and self._visible

    @property
    def position(self, median_size=None, auto_median=True):
        if auto_median:
            median_size = self.median_selector(median_size)
        self._latest_coords = (np.median(self.x[:median_size]), np.median(self.y[:median_size]))
        return self._latest_coords

    @property
    def marker_position(self, median_size=None, auto_median=True):
        if auto_median:
            median_size = self.median_selector(median_size)
        return np.median(self.side_x[:median_size]), np.median(self.side_y[:median_size])

    @property
    def heading(self, median_size=None, auto_median=True):
        if auto_median:
            median_size = self.median_selector(median_size)
        self._latest_angle = np.median(self.angle[:median_size]) % 360
        return self._latest_angle + marker_angle_offset

    @property
    def latest_values(self):
        return self._latest_values

    @property
    def coordinates(self, median_size=None, auto_median=True):
        if auto_median:
            median_size = self.median_selector(median_size)
        self._latest_coords = (np.median(self.x[:median_size]), np.median(self.y[:median_size]))
        return np.median(self.x[:median_size]), np.median(self.y[:median_size]), \
               np.median(self.side_x[:median_size]), np.median(self.side_y[:median_size])


    def grabbing_zone(self, role='unknown', median_size=None, auto_median=True, scale=1.):
        """
        SLIGHTLY OUTDATED:
        Returns x, y for the bottom left point of the rectangular grabber zone (p0_x) and
        x, y for top right point of the grabber zone.
        :param median_size:     optional. defaults to queue_size
        :param auto_median:     optional. defaults to True, to use automatic median selection.
        :param scale:           scale of the grabbing zone.
        :return: p0_x, p0_y, p1_x, p1_y
        """
        # TODO: check this when changing properties
        heading = self.heading
        x, y = self.position

        if role != 'enemy':
            center_x = x + (MIDPOINT_TO_BALL_ZONE + BALL_ZONE_HEIGHT * 0.5 * scale) * cos(radians(heading))
            center_y = y + (MIDPOINT_TO_BALL_ZONE + BALL_ZONE_HEIGHT * 0.5 * scale) * sin(radians(heading))
            return (center_x, center_y), (BALL_ZONE_WIDTH * scale, BALL_ZONE_HEIGHT * scale), heading + 90
        else:
            return (x, y), (ROBOT_HEIGHT * scale, ROBOT_WIDTH * scale), heading + 90


    def other_zone(self, zone, median_size=None, auto_median=True, scale=1.):
        """
        :param zone:            ["left", "right", "bottom"]
        :param median_size:
        :param auto_median:
        :param scale:
        :return:    (x,y), (w, h), heading
        """
        # TODO: check this when changing properties
        if zone == "left":
            heading = (self.heading - 90) % 360
            h = SIDE_ZONE_HEIGHT
            w = SIDE_ZONE_WIDTH
        elif zone == "right":
            heading = (self.heading + 90) % 360
            h = SIDE_ZONE_HEIGHT
            w = SIDE_ZONE_WIDTH
        elif zone == "bottom":
            heading = (self.heading + 180) % 360
            h = BACK_ZONE_HEIGHT
            w = BACK_ZONE_WIDTH
        x, y = self.position

        center_x = x + (MIDPOINT_TO_BALL_ZONE + h * 0.5 * scale) * cos(radians(heading))
        center_y = y + (MIDPOINT_TO_BALL_ZONE + h * 0.5 * scale) * sin(radians(heading))

        return (center_x, center_y), (w * scale, h * scale), heading + 90


    @property
    def predicted_ball_pos(self, median_size=None, auto_median=True):
        """
        returns a tuple of predicted position where the robot might be holding the ball.
        :return: ball_x, ball_y
        """
        # TODO: check this when changing properties
        heading = self.heading
        x, y = self.position

        ball_x = x + MIDPOINT_TO_BALL_ZONE * cos(radians(heading))
        ball_y = y + MIDPOINT_TO_BALL_ZONE * sin(radians(heading))

        return ball_x, ball_y


    def is_pos_in_close_distance_to_robot(self, x, y):
        """
        :param x:
        :param y:
        :return: True, if (x, y) is closer to robot than (MIDPOINT_TO_BALL_ZONE + BALL_ZONE_HEIGHT)
        """
        robot_x, robot_y = self.position
        if (robot_x - x)**2 + (robot_y - y)**2 > (MIDPOINT_TO_BALL_ZONE + BALL_ZONE_HEIGHT)**2:
            return False
        return True

    def is_point_in_grabbing_zone(self, x, y, role='unknown', scale=1., circular=True):
        """
        Checks that the given coordinates are in the hardcoded grabbing zone.
        :param x:
        :param y:
        :param scale:       scale of the grabbing zone.
        :param circular:    True if semicircular zone is required. It's furthest point coincides with old zone's.
            Effectively, zone is smaller because of that.
        :return: True or False
        """

        (z_x, z_y), (w, h), heading = self.grabbing_zone(role, scale=scale)
        heading = radians(heading - 90)

        # Top left
        ax = z_x + h/2. * cos(heading) + w/2. * cos(heading - radians(90))
        ay = z_y + h/2. * sin(heading) + w/2. * sin(heading - radians(90))

        # Top left
        bx = z_x + h/2. * cos(heading) + w/2. * cos(heading + radians(90))
        by = z_y + h/2. * sin(heading) + w/2. * sin(heading + radians(90))

        # Bottom right
        dx = z_x - h/2. * cos(heading) + w/2. * cos(heading - radians(90))
        dy = z_y - h/2. * sin(heading) + w/2. * sin(heading - radians(90))

        # Pseudo-magically calculate if the point is in the rectangle
        # http://stackoverflow.com/questions/2752725/finding-whether-a-point-lies-inside-a-rectangle-or-not

        bax = bx - ax
        bay = by - ay
        dax = dx - ax
        day = dy - ay

        # Could maybe check if a range of values from this coord is in grabbing zone, ball radius 4.2

        # Midpoint
        # if (x - ax) * bax + (y - ay) * bay < 0.0: return False
        # if (x - bx) * bax + (y - by) * bay > 0.0: return False
        # if (x - ax) * dax + (y - ay) * day < 0.0: return False
        # if (x - dx) * dax + (y - dy) * day > 0.0: return False

         # Top
        if (x - ax) * bax + (y + 4.2 - ay) * bay < 0.0: return False
        if (x - bx) * bax + (y + 4.2 - by) * bay > 0.0: return False
        if (x - ax) * dax + (y + 4.2 - ay) * day < 0.0: return False
        if (x - dx) * dax + (y + 4.2 - dy) * day > 0.0: return False

         # Bottom
        if (x - ax) * bax + (y - 4.2 - ay) * bay < 0.0: return False
        if (x - bx) * bax + (y - 4.2 - by) * bay > 0.0: return False
        if (x - ax) * dax + (y - 4.2 - ay) * day < 0.0: return False
        if (x - dx) * dax + (y - 4.2 - dy) * day > 0.0: return False

         # Left
        if (x - 4.2 - ax) * bax + (y - ay) * bay < 0.0: return False
        if (x - 4.2 - bx) * bax + (y - by) * bay > 0.0: return False
        if (x - 4.2 - ax) * dax + (y - ay) * day < 0.0: return False
        if (x - 4.2 - dx) * dax + (y - dy) * day > 0.0: return False

         # Right
        if (x + 4.2 - ax) * bax + (y - ay) * bay < 0.0: return False
        if (x + 4.2 - bx) * bax + (y - by) * bay > 0.0: return False
        if (x + 4.2 - ax) * dax + (y - ay) * day < 0.0: return False
        if (x + 4.2 - dx) * dax + (y - dy) * day > 0.0: return False

        if circular and not self.is_pos_in_close_distance_to_robot(x, y):
            return False

        return True


    def is_point_in_other_zone(self, x, y, zone, role, scale=1.):
        """
        Checks that the given coordinates are in the side or bottom zone.
        :param x:
        :param y:
        :param zone:        ["left", "right", "bottom"]
        :param scale:       scale of the grabbing zone.
        :return: True or False
        """

        if self.is_point_in_grabbing_zone(x, y, role):
            return False

        (z_x, z_y), (w, h), heading = self.other_zone(zone, scale=scale)
        heading = radians(heading - 90)

        # Top left
        ax = z_x + h/2. * cos(heading) + w/2. * cos(heading - radians(90))
        ay = z_y + h/2. * sin(heading) + w/2. * sin(heading - radians(90))

        # Top left
        bx = z_x + h/2. * cos(heading) + w/2. * cos(heading + radians(90))
        by = z_y + h/2. * sin(heading) + w/2. * sin(heading + radians(90))

        # Bottom right
        dx = z_x - h/2. * cos(heading) + w/2. * cos(heading - radians(90))
        dy = z_y - h/2. * sin(heading) + w/2. * sin(heading - radians(90))

        # Pseudo-magically calculate if the point is in the rectangle
        # http://stackoverflow.com/questions/2752725/finding-whether-a-point-lies-inside-a-rectangle-or-not

        bax = bx - ax
        bay = by - ay
        dax = dx - ax
        day = dy - ay

        # Could maybe check if a range of values from this coord is in grabbing zone, ball radius 4.2

        # Midpoint
        # if (x - ax) * bax + (y - ay) * bay < 0.0: return False
        # if (x - bx) * bax + (y - by) * bay > 0.0: return False
        # if (x - ax) * dax + (y - ay) * day < 0.0: return False
        # if (x - dx) * dax + (y - dy) * day > 0.0: return False

         # Top
        if (x - ax) * bax + (y + 4.2 - ay) * bay < 0.0: return False
        if (x - bx) * bax + (y + 4.2 - by) * bay > 0.0: return False
        if (x - ax) * dax + (y + 4.2 - ay) * day < 0.0: return False
        if (x - dx) * dax + (y + 4.2 - dy) * day > 0.0: return False

         # Bottom
        if (x - ax) * bax + (y - 4.2 - ay) * bay < 0.0: return False
        if (x - bx) * bax + (y - 4.2 - by) * bay > 0.0: return False
        if (x - ax) * dax + (y - 4.2 - ay) * day < 0.0: return False
        if (x - dx) * dax + (y - 4.2 - dy) * day > 0.0: return False

         # Left
        if (x - 4.2 - ax) * bax + (y - ay) * bay < 0.0: return False
        if (x - 4.2 - bx) * bax + (y - by) * bay > 0.0: return False
        if (x - 4.2 - ax) * dax + (y - ay) * day < 0.0: return False
        if (x - 4.2 - dx) * dax + (y - dy) * day > 0.0: return False

         # Right
        if (x + 4.2 - ax) * bax + (y - ay) * bay < 0.0: return False
        if (x + 4.2 - bx) * bax + (y - by) * bay > 0.0: return False
        if (x + 4.2 - ax) * dax + (y - ay) * day < 0.0: return False
        if (x + 4.2 - dx) * dax + (y - dy) * day > 0.0: return False

        return True


    def angle_of_line(self, point1, point2):
        point2 = list(point2-point1)
        return degrees(atan2(point2[1], point2[0]))


    def _get_angle(self):
        """
        Gets angle between 2 points.
        :return: angle, from 0 to 360 degrees
        """
        x, y, sx, sy = self.coordinates
        angle = self.angle_of_line(np.array([x, y]),
                                 np.array([sx, sy]))
        # Correct for marker offset
        return (angle + self.offset_angle + 90) % 360

    def get_other_coordinates(self):
        """
        Do not use for calculations. These coords don't use the median.
        :return: [(x0, y0), (x1, y1), (x2, y2)]. Might be smaller if less circles are found.
        """
        stuff = np.array(self.other_coords, np.int32)
        stuff = stuff.reshape((-1,1,2))
        return stuff

    def reset(self):
        self.x = list()
        self.y = list()
        self.side_x = list()
        self.side_y = list()
        self.other_coords = list()

    def __str__(self):
        return "Robot '%s' at (%s,%s)"%(self.name, self.x, self.y)

    @staticmethod
    def px_to_cm(px):
        return np.array([px[0] * (128.0/260),
                         px[1] * (128.0/270)])
    @staticmethod
    def cm_to_px(cm):
        return np.array([cm[0] * (260/128.0),
                         cm[1] * (270/128.0)])


    def median_selector(self, max_median=None):
        """
        :param max_median:  maximum top bound for median number <= queue_size
        :return: int        smallest adequate median length <= queue_size
        """

        # Get latest data
        l_angle = self._latest_angle % 360
        l_x, l_y = self._latest_coords

        # Determine loop parameters
        q_size = self.queue_size
        if max_median and 0 < max_median < q_size:
            q_size = max_median

        # Loop over medians until you find an acceptable one or reach the end
        for m in xrange(1, q_size):
            if abs(np.median(self.angle[:m]) % 360 - l_angle) < MEDIAN_SWITCH_ANGLE_THRESHOLD and \
                (np.median(self.x[:m]) - l_x)**2 + (np.median(self.y[:m]) - l_y)**2 < MEDIAN_SWITCH_DISTANCE_THRESHOLD**2:
                    return m

        return q_size
