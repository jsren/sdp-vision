__author__ = 's1210443'

import os
import time
import cv2
from vision.colors import BGR_COMMON
import numpy as np
from math import cos, sin, pi

# use log function to print something that changes often


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

groups = {}


def special_str(s, type):
    return type + str(s) + bcolors.ENDC


def log(name, value, group = "general"):
    if group not in groups:
        groups[group] = {}
    groups[group][name] = value

def log_time(group, name = 'time'):
    if group not in groups:
        groups[group] = {}
    localtime = time.asctime( time.localtime(time.time()) )
    groups[group][name] = localtime





dots = {}
lines = {}

class Dot:
    def __init__(self, pos, col):
        self.pos = pos
        self.col = col

def log_dot(position, color, id):
    bla = Dot(position, color)
    dots[id] = bla

def log_line(pos2d, id):
    lines[id] = pos2d


def log_pos_angle(pos, angle, id, length=40.0):
    log_dot(pos, 'yellow', id)


    da = np.array([cos(angle), sin(angle)]) * length
    log_line([pos, pos + da], id)

def draw_line(frame, points, thickness=2):
    p0 = [int(x) for x in points[0]]
    p1 = [int(x) for x in points[1]]
    if points is not None:
        cv2.line(frame, flip_pos(frame, p0), flip_pos(frame, p1), BGR_COMMON['red'], thickness)


def flip_pos(frame, t):
    return t[0], len(frame) - t[1]

def draw_dots(frame):
    for k, v in dots.iteritems():
        cv2.circle(
                frame, (int(v.pos[0]), int(len(frame)-v.pos[1])),
                4, BGR_COMMON[v.col], -1)

    for k,v in lines.iteritems():
        draw_line(frame, v)

    return frame


def draw():
    clear = "\n" * 50
    print clear
    print(special_str('NOTE: ', bcolors.BOLD) + 'vision window has to be active window in order for key input to work')

    # won't work on windows
    # os.system('clear')
    for k,v in groups.iteritems():
        print(special_str(k + "-----------", bcolors.BOLD))
        for k,v in v.iteritems():
            line = str(k) + ": "
            if isinstance(v, bool):
                line += special_str(v, bcolors.OKGREEN if v else bcolors.FAIL)
            else:
                line += str(v)
            print(line)
        print(special_str("----------------", bcolors.BOLD))
