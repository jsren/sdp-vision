from math import degrees, atan2
import numpy as np

# Angle offset of marker on top plate.
# Not sure if clockwise or anti-clockwise.
marker_angle_offset = 34.509


class RobotInstance(object):

    def __init__(self, name, m_color, s_color, offset_angle, present=False):
        """
        DO NOT USE OTHER CIRCLE COORDINATES FOR CALCULATIONS - THEY'RE NOT IN A QUEUE
        """
        self.queue_size = 1
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
    def position(self, median_size=None):
        return np.median(self.x[:median_size]), np.median(self.y[:median_size])

    @property
    def marker_position(self, median_size=None):
        return np.median(self.side_x[:median_size]), np.median(self.side_y[:median_size])

    @property
    def heading(self, median_size=None):
        return np.median(self.angle[:median_size]) % 360

    @property
    def latest_values(self):
        return self._latest_values

    @property
    def coordinates(self, median_size=None):
        return np.median(self.x[:median_size]), np.median(self.y[:median_size]), \
               np.median(self.side_x[:median_size]), np.median(self.side_y[:median_size])

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


