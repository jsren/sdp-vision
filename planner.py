import new
import serial
import numpy as np

from math import degrees, atan2,tan,radians,copysign
from threading import Thread
from interface import VisionInterface,RobotType
import time

# import sys, os.path as path
# sys.path.append(path.join(path.dirname(__file__), "vision"))


# TODO: DELETE THIS SHIT
BALL_SIZE             = 5.2
ROBOT_SIZE            = 20.0
INITDISPLACEMENT      = 0.0
GRABBER_LENGTH        = 8.0
visionInformation     = list()
lastEuclideanDistance = 0.0

# TODO: DISTANCE OF THE ROBOT FROM THE BALL AND THE SPIN
CLOSE_DISTANCE = GRABBER_LENGTH * 0.8 - BALL_SIZE/2
OPEN_DISTANCE  = GRABBER_LENGTH + BALL_SIZE + 1

# TODO: Disable on release
assert CLOSE_DISTANCE <= GRABBER_LENGTH
assert OPEN_DISTANCE - GRABBER_LENGTH >= BALL_SIZE


# ==============================================================
# =================       OPEN SERIAL      =====================
# ==============================================================
class DummySerial(object):
    timeout = 0
    def write(self, x): pass
    def read(self): return [0]
    def read_all(self): return [0]

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
except:
    print "[WARNING] Cannot open port: reverting to dummy serial"
    ser = DummySerial()
# ==============================================================

# 379, 439
class DummyVision(object):
    def get_robot_midpoint(self):
        return _robotpos
    def get_side_circle(self):
        return _circlepos
    def get_ball_pos(self):
        return _ballpos


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
    return degrees(atan2(point2[1]-point1[1], point2[0]-point1[0]))

def sendCommand(cmd, timeout=0.1):
    while True:
        ser.timeout = timeout
        ser.write(cmd+'\n')
        bytes = ser.read()

        # Probably a timeout
        if len(bytes) == 0:
            ser.write("cancel\n")
            return ser.read()

        # Success, end loop
        elif bytes[0] == 0:
            return 0




def rotateVector(vector, angle):
    theta = (angle/180.0) * np.pi

    rotMatrix = np.array([[np.cos(theta), np.sin(theta)],
                         [-np.sin(theta), np.cos(theta)]])
    return list(np.dot(rotMatrix, np.array(vector)))

def orientRobot(current, target):
    d = target - current
    ser.write("(0,0,"+str(int(d))+")\n")
    time.sleep(1)
    something = ser.read(4) #https://s3.amazonaws.com/static.carthrottle.com/workspace/uploads/comments/15dca6d3e25e1fc749d05b69aac8e7fc.png
    print something
    #_sim_update_robotrot(d)


class Planner:
    #TODO: might need GOAL COORDINATES
    def __init__(self, vision_interface):
        self.vision = vision_interface

        # Attach heading function
        #self.vision.get_robot_heading = new.instancemethod(
        #    get_robot_heading, self.vision, self.vision.__class__)

    def px_to_cm(self,px):
        return np.array([px[0] * (300.0/self.vision.pitch_dimensions[0]),px[1] * (220.0/ self.vision.pitch_dimensions[1])])
    def cm_to_px(self,cm):
        return np.array([cm[0] * (self.vision.pitch_dimensions[0]/300.0),
                     cm[1] * (self.vision.pitch_dimensions[1]/220.0)])


    # returns a LIST of enemy robot information
    def getEnemyRobots(self,number):
        listOfRobots =  [r for r in self.vision.get_robots() if r.type == RobotType.ENEMY and r.visible]
        while (True):
            if (len(listOfRobots) == number):
                return listOfRobots
            listOfRobots = [r for r in self.vision.get_robots() if r.type == RobotType.ENEMY]


    # returns my robot information
    def getMyRobot(self):
        listOfRobots = [r for r in self.vision.get_robots() if r.type == RobotType.OURS]
        while (True):
            if(len(listOfRobots) == 1):
                return listOfRobots[0]
            listOfRobots = [r for r in self.vision.get_robots() if r.type == RobotType.OURS]

     # returns teammate information
    def getTeammate(self):
        print 'Start temmate'
        listOfRobots = [r for r in self.vision.get_robots() if r.type == RobotType.FRIENDLY ]
        while (True):
            if(len(listOfRobots) == 1):
                print 'Done Friendly'
                return listOfRobots[0]
            listOfRobots = [r for r in self.vision.get_robots() if r.type == RobotType.FRIENDLY]

    # returns the euclidean distance between our robot and the ball
    def ball_distance(self):
       ballpos  = np.array(self.vision.get_ball_position())
       midpoint = np.array(self.getMyRobot().position)
       ball_dist = np.linalg.norm(self.px_to_cm(ballpos - midpoint)) - ROBOT_SIZE/2.0
       return ball_dist

    def begin_task1(self):
        t = Thread(target=self.task1)
        t.start()
        return t

    def task1(self):
        global lastEuclideanDistance
        grabbersOpen = False
        # Reset robot rotation
        robot_heading = self.getMyRobot().heading
        #TODO: obtain functions for ball and robot position - DONE - NEEDS TESTING
        robot_pos = self.getMyRobot().position
        ball_pos = self.vision.get_ball_position()
        required_robot_heading = angleOfLine(robot_pos,ball_pos)
        while not valueInRange(robot_heading, required_robot_heading, 6.0):
            orientRobot(robot_heading, required_robot_heading)
            ser.timeout = 1
            s = ser.read_all()
            while len(s) == 0:
                s = ser.read_all()
            robot_heading = self.getMyRobot().heading

        # Oversee ball-grabbing
        complete = False
        while not complete:
            #TODO: Get the output from vision system. - DONE NEEDS TESTING
            ballpos  = self.vision.get_ball_position()
            midpoint = self.getMyRobot().position

            robot_heading = self.getMyRobot().heading
            angle_to_ball = angleOfLine(midpoint, ballpos)

            # TODO: Check threshold

            facing_ball = valueInRange(robot_heading, angle_to_ball, 5)
            ball_dist   = self.ball_distance()

            # Ball inside grabbers, grabbers open
            if ball_dist <= CLOSE_DISTANCE and facing_ball and grabbersOpen:
                ser.write('close\n')
                complete = True

            # Ball outside grabbers, close by, grabbers open
            elif ball_dist <= OPEN_DISTANCE and facing_ball and grabbersOpen:
                dy = ball_dist * 0.8
                ser.write("(" + str(int(dy)) + ",0,0)\n")
                #_sim_update_robotpos(np.array([0, dy]))

            elif ball_dist <= OPEN_DISTANCE and facing_ball and not grabbersOpen:
                ser.write("open\n")
                grabbersOpen = True

            elif ball_dist <= OPEN_DISTANCE and not facing_ball:
                orientRobot(robot_heading, angle_to_ball)

            else:
                distance = self.ball_distance() - OPEN_DISTANCE
                ser.write("(0,"+str(int(distance))+"0)\n")


            # checks what arduino is doing
            ser.timeout = 3
            s = ser.read()
            while len(s) < 1:
                if s[0] == 255: break # Cancelled

                ball_dist = self.ball_distance()

                if ball_dist >= lastEuclideanDistance + 5:
                    ser.write("cancel\n")
                else:
                    lastEuclideanDistance = ball_dist
                s = ser.read()



    def begin_task3(self):
        t = Thread(target=self.task3)
        t.start()
        return t

    def task3(self):
        while True:
            midpoint      = self.getMyRobot().position
            robot_heading = self.getMyRobot().heading
            #TODO: get self.pitch - update 2.0
            angle_to_goal = angleOfLine(midpoint, self.pitch['their_goal'])

            while not valueInRange(robot_heading, angle_to_goal, 10):
                orientRobot(robot_heading, angle_to_goal)
                robot_heading = self.getMyRobot().heading

            distance = 150

        #TODO:GET UPDATE IF PERFORMED
        #if sendCommand("open", timeout=1) == 255: continue
        #if sendCommand("->"+str(distance), timeout=1) == 255: continue
        return

    def begin_task4(self):
        t = Thread(target=self.task4,args=(self.getTeammate(),))
        t.start()
        return t

    # PARAMS: robot to receive pass from
    # turns the robot to make him face the teammate, and receive the pass
    def task4(self,robot):
        print "Start "
        robot_heading = self.getMyRobot().heading
        #todo: check if orientRobot takes any angle!!! CHECK WHAT KIND OF ANGLE DOES ROBOT.HEADING RETURN
        required_direction = - copysign(180.0, robot.heading) + robot.heading
        while not valueInRange(robot_heading, required_direction, 6.0):
            orientRobot(robot_heading, required_direction)
            #ser.timeout = 1
            #s = ser.read()
            #while len(s) == 0:
                #s = ser.read()
            robot_heading = self.getMyRobot().heading
        ser.write("open\n")
        grabbersOpen = True
        ball_dist = self.ball_distance()
        while(ball_dist > 10.0):
            ball_dist = self.ball_distance()
        ser.write("close\n")
        grabbersOpen = False
        ball_dist = self.ball_distance()
        #TODO: might use Robot.has_ball()
        if(ball_dist > 3.0):
            self.task1()

    def begin_task5(self):
        t = Thread(target=self.task5)
        t.start()
        return t

    # receives the pass, turns to the teammate and makes a pass
    def task5(self):
        self.task4(self.getEnemyRobots(1)[0])
        robot_heading = self.getMyRobot().heading
        teammate_robot_heading = self.getTeammate().heading
        while not valueInRange(robot_heading,teammate_robot_heading,6):
            orientRobot(robot_heading, teammate_robot_heading)
            '''
            ser.timeout = 1
            s = ser.read()
            while len(s) == 0:
                s = ser.read()
            '''
            robot_heading = self.getMyRobot().heading
        ser.write("->150\n")


    def begin_task6(self):
        t = Thread(target=self.task6)
        t.start()
        return t


    def task6(self):
       enemyRobots = self.getEnemyRobots(2)
       opponent1_pos =enemyRobots[0].position
       opponent2_pos =enemyRobots[1].position
       our_robot_pos =self.getMyRobot().position
       required_robot_position_y = ((opponent2_pos[1] - opponent1_pos[1])/(opponent2_pos[0] - opponent1_pos[0]))*(our_robot_pos[0] - opponent1_pos[0]) + opponent1_pos[1]
       #TODO:RECHECK PIXELS
       #moving_distance = (required_robot_position_y - our_robot_pos[1])*(220.0/379)
       moving_distance = px_to_cm(np.array((0,required_robot_position_y)) - np.array((0,our_robot_pos[1])))[1]
       ser.write("(" + str(int(moving_distance)) + ",0,0)\n")

    def begin_task7(self):
        t = Thread(target=self.task7)
        t.start()
        return t


    def task7(self):
        myRobotPos = self.getMyRobot().position
        enemyRobot = self.getEnemyRobots(1)[0]
        #TODO:RECHECK PIXELS
        x = myRobotPos[0] - enemyRobot.position[0]
        y2 = enemyRobot.position[1] + tan(radians(enemyRobot.heading))*x
        moveDistance = px_to_cm(np.array((0,y2)) - np.array((0,myRobotPos[1])))[1]
        ser.write("(" + str(int(moveDistance)) + ",0,0)\n")





#TODO:FLUSH INFORMATION GET FROM JAMES main,delete pitc

pitch = {
        #'pitch_width' : 250,
        #'pitch_height': 150,
        #'our_goal'    : np.array([0, 75]),
        'their_goal'  : np.array([250.0, 75.0])
    }

ser.read_all()
ser.write("remote\n")
ser.flushOutput()
ser.flushInput()
ser.read_all()

vision = VisionInterface(1, 'big')
vision.launch_vision()
vision.wait_for_start()
planner = Planner(vision)


command = raw_input("Input command: ")
while (command != 'quit'):
    if (command == 'task1' or command == 'task2'):
        planner.begin_task1()
    elif (command == 'task3'):
        planner.begin_task3()
    elif (command == 'task4'):
        planner.begin_task4()
    elif (command == 'task5'):
        planner.begin_task5()
    elif (command == 'task6'):
        planner.begin_task6()
    elif (command == 'task7'):
        planner.begin_task7()
    else:
        print "Unknown command"
    print "Done"
    command = raw_input("Input next command: ")





if __name__ == "__main__":
    print "[INFO] Beginning *SIMULATION*"

    _robotpos  = np.array([10.0, 10.0])
    _circlepos = np.array([10.0, 12.5])
    _ballpos   = np.array([50.0, 20.0])

    pitch = {
        #'pitch_width' : 250,
        #'pitch_height': 150,
        #'our_goal'    : np.array([0, 75]),
        'their_goal'  : np.array([250.0, 75.0])
    }

    # Initiate remote control on robot
    ser.write("remote\n")

    planner = Planner(DummyVision(), pitch)
    print "[INFO] Beginning task 1 simulation"
    planner.task1()
    print "[INFO] Beginning task 3 simulation"
    planner.task3()
    print "[INFO] Beginning task 5 simulation"
    planner.task5()





