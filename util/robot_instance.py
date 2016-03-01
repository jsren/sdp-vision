from math import degrees, atan2
import numpy as np

# Angle offset of marker on top plate.
# Not sure if clockwise or anti-clockwise.
marker_angle_offset = 34.509


class RobotInstance(object):

    def __init__(self, name, m_color, s_color, present=False):
        """
        DO NOT USE OTHER CIRCLE COORDINATES FOR CALCULATIONS - THEY'RE NOT IN A QUEUE
        """
        self.queue_size = 4
        self.x = list()
        self.y = list()
        self.main_color = m_color
        self.side_color = s_color
        self.name = name
        self.side_x = list()
        self.side_y = list()
        self.age = 0
        self.angle = list()
        self.other_coords = list()

        self._visible = False
        self._present = bool(present)

    def update(self, x, y, m_color, s_color, side_x, side_y, other_coords):
        if self.main_color == m_color and self.side_color == s_color:
            self.x.insert(0, x); self.x = self.x[:self.queue_size]
            self.y.insert(0, y); self.y = self.y[:self.queue_size]
            self.side_y.insert(0, side_y); self.side_y = self.side_y[:self.queue_size]
            self.side_x.insert(0, side_x); self.side_x = self.side_x[:self.queue_size]
            self.angle.insert(0, self._get_angle()); self.angle = self.angle[:self.queue_size]
            self.other_coords = other_coords
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
    def position(self):
        return np.median(self.x), np.median(self.y)

    @property
    def marker_position(self):
        return np.median(self.side_x), np.median(self.side_y)

    @property
    def heading(self):
        return np.median(self.angle)

    def get_coordinates(self):
        return np.median(self.x), np.median(self.y), \
               np.median(self.side_x), np.median(self.side_y)

    def angleOfLine(self, point1, point2):
        point2 = list(point2-point1)
        return degrees(atan2(point2[1], point2[0]))

    def _get_angle(self):
        # Get angle between points
        x, y, sx, sy = self.get_coordinates()
        angle = self.angleOfLine(np.array([x, y]),
                                 np.array([sx, sy]))
        # Correct for marker offset
        return angle + marker_angle_offset + 90

    def get_robot_heading(self):
        return np.median(self.angle)

    def get_other_coordinates(self):
        """
        Do not use for calculations. These coords don't use the median.
        :return: [(x0, y0), (x1, y1), (x2, y2)]. Might be smaller if less circles are found.
        """
        return self.other_coords

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


