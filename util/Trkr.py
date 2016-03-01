

class Trkr(object):

    def __init__(self, calibration, color, target):
        self.calibration = calibration
        self.color       = color
        self.target      = tuple(target)

    def update(self, frame):




