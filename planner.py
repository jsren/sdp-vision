import new
import serial
import numpy as np
import time

from math import degrees, atan2, isnan
from threading import Thread

def px_to_cm(px, py):
    return np.array([px * (128.0/260),
                     py * (128.0/270)])
def cm_to_px(cmx, cmy):
    return np.array([cmx * (260/128.0),
                     cmy * (270/128.0)])

# TODO: DELETE THIS SHIT
BALL_SIZE             = cm_to_px(5.2, 5.2)
ROBOT_SIZE            = cm_to_px(20.0, 20.0)
INITDISPLACEMENT      = 34.5
GRABBER_LENGTH        = cm_to_px(0, 8.0)[1]
visionInformation     = list()
lastEuclideanDistance = 0.0

# TODO: DISTANCE OF THE ROBOT FROM THE BALL AND THE SPIN
CLOSE_DISTANCE = GRABBER_LENGTH * 0.8 - BALL_SIZE[1]/2
OPEN_DISTANCE  = GRABBER_LENGTH + BALL_SIZE[1] + 1

# TODO: Disable on release
assert CLOSE_DISTANCE <= GRABBER_LENGTH
assert OPEN_DISTANCE - GRABBER_LENGTH >= BALL_SIZE[1]


# ==============================================================
# =================       OPEN SERIAL      =====================
# ==============================================================
class DummySerial(object):
    timeout = 0
    def write(self, x):
        print "[CMD] '%s'"%x
        time.sleep(1)
    def read(self): return [0]

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
except:
    print "[WARNING] Cannot open port: reverting to dummy serial"
    ser = DummySerial()
# ==============================================================

class DummyVision(object):
    def get_robot_midpoint(self):
        return _robotpos
    def get_side_circle(self):
        return _circlepos
    def get_ball_position(self):
        return _ballpos
    def wait_for_start(self):
        pass

if __name__ == "__main__":
    _ballpos   = None
    _robotpos  = None
    _circlepos = None

    def _sim_update_robotpos(nparray_delta):
        global _robotpos, _circlepos
        _robotpos += nparray_delta
        _circlepos += nparray_delta

    def _sim_update_robotrot(degree_delta):
        global _robotpos, _circlepos
        v = rotateVector(_circlepos - _robotpos, degree_delta)
        _circlepos = _robotpos + v

else:
    def _sim_update_robotpos(nparray_delta): pass
    def _sim_update_robotrot(degree_delta): pass



# Negative center not applicable
def valueInRange(x, center, range):
    if range < 0: range = -range
    return (x >= center - range) and (x <= center + range)


def angleOfLine(point1, point2):
    point2 = point2 - point1
    return degrees(atan2(point2[1], point2[0]))


def get_robot_heading(self):
    # Get angle between points

    angle = angleOfLine(self.get_robot_midpoint(),
                        self.get_side_circle())
    # Correct for marker offset
    return angle + INITDISPLACEMENT + 90


def rotateVector(vector, angle):
    theta = (angle/180.0) * np.pi

    rotMatrix = np.array([[np.cos(theta), np.sin(theta)],
                         [-np.sin(theta), np.cos(theta)]])
    return list(np.dot(rotMatrix, np.array(vector)))

def orientRobot(current, target):
    d = target - current
    if not isnan(d):
        ser.write("(0,0,"+str(int(d))+")\n")
        ser.flush()
        _sim_update_robotrot(d)


def sendCommand(cmd, timeout=0.1):
    while True:
        ser.timeout = timeout
        ser.write(cmd+'\n')
        ser.flush()
        bytes = ser.read()

        # Probably a timeout
        if len(bytes) == 0:
            ser.write("cancel\n")
            ser.flush()
            return ser.read()

        # Success, end loop
        elif bytes[0] == 0:
            return 0


class Planner:

    def __init__(self, vision_interface, pitch_setup):
        self.vision = vision_interface
        self.pitch  = pitch_setup

        # Attach heading function
        self.vision.get_robot_heading = new.instancemethod(
            get_robot_heading, self.vision, self.vision.__class__)


    def begin_task1(self):
        t = Thread(target=self.task1)
        t.start()
        return t

    def task1(self):
        global lastEuclideanDistance
        grabbersOpen = False

        self.vision.wait_for_start()

        ser.write("remote\n")
        ser.flush()


        #TODO: ensure that we are facing always the same direction -THE VALUE IS 0
        # Reset robot rotation
        robot_heading = self.vision.get_robot_heading()
        while not valueInRange(robot_heading, 0, 6.0) and False:
            orientRobot(robot_heading, 0)
            ser.timeout = 1
            s = ser.read()
            while len(s) == 0:
                s = ser.read()
            robot_heading = self.vision.get_robot_heading()

        # Oversee ball-grabbing
        complete = False
        while not complete:
            #TODO: Get the output from vision system.
            ballpos  = self.vision.get_ball_position()
            midpoint = self.vision.get_robot_midpoint()

            robot_heading = self.vision.get_robot_heading()
            angle_to_ball = angleOfLine(midpoint, ballpos)

            # TODO: Check threshold
            facing_ball = valueInRange(robot_heading, angle_to_ball, 5)
            ball_dist   = np.linalg.norm(ballpos - (midpoint + np.array([0, (ROBOT_SIZE/2)[1]])))

            # Ball inside grabbers, grabbers open
            if ball_dist <= CLOSE_DISTANCE and facing_ball and grabbersOpen:
                ser.write('close\n')
                complete = True

            # Ball outside grabbers, close by, grabbers open
            elif ball_dist <= OPEN_DISTANCE and facing_ball and grabbersOpen:
                dy = ball_dist * 0.8
                ser.write("(" + str(int(px_to_cm(0, dy)[1])) + ",0,0)\n")
                _sim_update_robotpos(np.array([0, dy]))

            elif ball_dist <= OPEN_DISTANCE and facing_ball and not grabbersOpen:
                ser.write("open\n")
                grabbersOpen = True

            elif ball_dist <= OPEN_DISTANCE and not facing_ball:
                orientRobot(robot_heading, angle_to_ball)

            else:
                # Adjust to be within x-range of ball
                if not valueInRange(midpoint[0], ballpos[0], 0.5*(ROBOT_SIZE[0] - BALL_SIZE[0])):
                    dx = (ballpos - midpoint)[0]
                    #dx += ROBOT_SIZE[0] / (2. if dx < 0 else -2.)
                    if not isnan(dx):
                        ser.write("(0,"+str(int(px_to_cm(dx, 0)[0]))+",0)\n")
                        _sim_update_robotpos(np.array([dx, 0]))

                # Adjust to be within 'opening' range of ball
                elif not valueInRange(midpoint[1] + ROBOT_SIZE[1]/2, ballpos[0], 0.5*(ROBOT_SIZE[1] - BALL_SIZE[1])):
                    dy = (ballpos - midpoint)[1] - OPEN_DISTANCE
                    dy += ROBOT_SIZE[1] / (2. if dy < 0 else -2.)

                    ser.write("(" + str(int(px_to_cm(0, dy)[1])) + ",0,0)\n")
                    _sim_update_robotpos(np.array([0, dy]))


            # checks what arduino is doing
            ser.flush()
            ser.timeout = 10
            s = ser.read()
            print s
            while len(s) < 1:
                ball_dist = np.linalg.norm(self.vision.get_ball_position()
                                           - self.vision.get_robot_midpoint())

                if ball_dist >= lastEuclideanDistance + 5:
                    ser.write("cancel\n")
                    ser.flush()
                else:
                    lastEuclideanDistance = ball_dist
                s = ser.read()



    def begin_task3(self):
        t = Thread(target=self.task3)
        t.start()
        return t

    def task3(self):
        self.vision.wait_for_start()

        ser.write("remote\n")
        ser.flush()

        while True:
            midpoint      = self.vision.get_robot_midpoint()
            robot_heading = self.vision.get_robot_heading()
            angle_to_goal = angleOfLine(midpoint, self.pitch['their_goal'])

            if not valueInRange(robot_heading, angle_to_goal, 10):
                orientRobot(robot_heading, angle_to_goal)

            distance = 150 # TODO: Get power

            if sendCommand("open", timeout=1) == 255: continue
            if sendCommand("->"+str(int(distance)), timeout=1) == 255: continue
            return



if __name__ == "__main__":
    print "[INFO] Beginning *SIMULATION*"

    _robotpos  = np.array([10.0, 10.0])
    _circlepos = np.array([10.0, 12.5])
    _ballpos   = np.array([50.0, 50.0])

    pitch = {
        #'pitch_width' : 250,
        #'pitch_height': 150,
        #'our_goal'    : np.array([0, 75]),
        'their_goal'  : np.array([250.0, 75.0])
    }

    # Initiate remote control on robot
    ser.write("remote\n")
    ser.flush()

    planner = Planner(DummyVision(), pitch)
    print "[INFO] Beginning task 1 simulation"
    planner.task1()
    print "[INFO] Beginning task 3 simulation"
    planner.task3()





