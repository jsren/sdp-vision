from math import degrees, atan2
import numpy as np

# Angle offset of marker on top plate.
# Not sure if clockwise or anti-clockwise.
marker_angle_offset = 34.509

MEDIAN_SWITCH_ANGLE_THRESHOLD = 25
MEDIAN_SWITCH_DISTANCE_THRESHOLD = 30

MIDPOINT_TO_BALL_ZONE = 10
BALL_ZONE_HEIGHT = 10
BALL_ZONE_WIDTH = 20

class RobotInstance(object):

    def __init__(self, name, m_color, s_color, offset_angle, present=False):
        """
        DO NOT USE OTHER CIRCLE COORDINATES FOR CALCULATIONS - THEY'RE NOT IN A QUEUE
        """
        self.queue_size = 5
        self.x = list()
        self.y = list()
        self.main_color = m_color
        self.side_color = s_color
        self.offset_angle = offset_angle  # individual error offset
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
        return self._latest_angle

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

    @property
    def grabbing_zone(self, median_size=None, auto_median=True):
        # TODO: check this when changing properties
        heading = self.heading
        x, y = self.position
        point_bottom_left_x = x + MIDPOINT_TO_BALL_ZONE * np.cos(heading) - 0.5 * BALL_ZONE_WIDTH * np.cos(heading + 90)
        point_bottom_left_y = y + MIDPOINT_TO_BALL_ZONE * np.sin(heading) - 0.5 * BALL_ZONE_WIDTH * np.sin(heading + 90)
        point_bottom_right_x = x + (MIDPOINT_TO_BALL_ZONE + BALL_ZONE_HEIGHT) * np.cos(heading) + 0.5 * BALL_ZONE_WIDTH * np.cos(heading + 90)
        point_bottom_right_y = y + MIDPOINT_TO_BALL_ZONE * np.sin(heading) + 0.5 * BALL_ZONE_WIDTH * np.sin(heading + 90)
        return (point_bottom_left_x, point_bottom_left_y),(point_bottom_right_x, point_bottom_right_y)




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
        return (angle + marker_angle_offset + self.offset_angle + 90) % 360

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
