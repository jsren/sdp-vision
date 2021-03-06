from util import Tracker, RobotInstance

from scipy.cluster.vq import kmeans
from Tkinter import *

from gui.common import UserVariable
from functools import partial

import cv2
import numpy as np


NUMBER_OF_MAIN_CIRCLES_PER_COLOR = 2
NUMBER_OF_SIDE_CIRCLES_PER_COLOR = 16

ROBOT_DISTANCE = 30

CORRECTION_STEP = 2             # Green
CORRECTION_MAX_DISTANCE = 3     # Blue
CORRECTION_AREA_RADIUS = 4      # Yellow


class TopPlate(object):

    def __init__(self, midpoint, markers):
        self.midpoint        = midpoint
        self.primary_color   = midpoint['color']
        self.secondary_color = markers[0]['color'] if any(markers) else None

        self.markers = list(markers)

        if len(markers) > 1:

            self.naive_midpoint = np.array([np.mean(np.array([
                p['pos'][0] - markers[0]['pos'][0]
                for p in markers[1:]])),
                                           np.mean(np.array([
                p['pos'][1] - markers[0]['pos'][1]
                for p in markers[1:]]))])

            self.naive_midpoint += np.array(markers[0]['pos'])

        else:
            self.naive_midpoint = np.array(self.midpoint['pos'])



class RobotTracker(Tracker):

    @property
    def hasUI(self):
        return True

    @property
    def title(self):
        return "Robot Tracker Settings"

    def __init__(self,
                 main_colors,
                 side_colors,
                 crop,
                 pitch,
                 calibration,
                 robots,
                 return_circles=False):
        """
        Tracks all circles of given colors and calls k-nn to find the robots. Maps each one into a different set,
        allowing the calling function to perform identification.
        :param main_colors:      [string] - list of central circle colors to look for
        :param main_colors:      [string] - list of side circle colors to look for
        :param crop         [(left-min, right-max, top-min, bot-max)] - crop coordinates
        :param pitch:       int - pitch number from [0, 1]
        :param calibration: dict - dictionary of calibration values
        :param return_circles: if true, returns all circle contours found, in addition to robot positions
        """

        self.main_colors    = main_colors
        self.side_colors    = side_colors
        self.colors         = main_colors + side_colors
        self.crop           = crop
        self.pitch          = pitch
        self.calibration    = calibration
        self.return_circles = return_circles
        self.robots         = robots



    def find_all_circles(self, frame):
        """
        Returns all colored circles found. Colors are set in calibrations.json
        :param frame:   Current camera frame
        :return:        {color:[circles]}
        """
        circles = dict()
        for color in set(self.colors):
            # Get all circles of the given colour
            cal = self.calibration[color]
            contours, hierarchy, mask = self.get_contours(frame.copy(), self.crop,
                   cal)

            circles[color] = contours

            # Get only the required number of colors.
            if color in self.main_colors:
                circles[color] = self.get_n_largest_contours(
                    NUMBER_OF_MAIN_CIRCLES_PER_COLOR, circles[color])

            elif color in self.side_colors:
                circles[color] = self.get_n_largest_contours(
                    NUMBER_OF_SIDE_CIRCLES_PER_COLOR, circles[color])

        return circles



    def find_color_clusters(self, circles_of_one_color, k, iter=20):
        """
        Returns k cluster centres of one color
        :param frame:   Current camera frame
        :param circles: [circles]
        :param k:       int, number of cluster centres
        :param iter:    int, number of times to iterate k-means
        :return:    [[(x,y)]] - coordinates of found centres
        """
        circles = []
        for crc in circles_of_one_color:
            (x, y), _ = cv2.minEnclosingCircle(crc)
            circles.append((x, y))
        circles = np.array(circles)

        try:
            return kmeans(circles, k, iter=iter)[0]
        except ValueError:
            return np.array([])



    def find(self, frame, queue):
        # Array of contours found.
        circles = self.find_all_circles(frame)

        # Use k-means to find cluster centres for main colors
        robot_results = []
        for m_color in self.main_colors:

            cls = self.find_color_clusters(circles[m_color], 2)
            if cls.any() and len(cls) == 2 and np.linalg.norm(cls[0] - cls[1]) > ROBOT_DISTANCE:

                # For each cluster, find near circles
                for cl in cls:
                    near_circles = { k : [] for k in self.side_colors }

                    for (color, subcircs) in circles.iteritems():
                        if color not in self.side_colors: continue

                        for circle in subcircs:
                            # Convert contour into circle
                            (x0, y0), _ = cv2.minEnclosingCircle(circle)

                            if (x0-cl[0])**2 + (y0-cl[1])**2 < ROBOT_DISTANCE**2:
                                near_circles[color].append(circle)


                    # Find the significant side circle & others
                    if len(near_circles[self.side_colors[0]]) == 0 or len(near_circles[self.side_colors[1]]) == 0:
                        continue
                    if len(near_circles[self.side_colors[0]]) > len(near_circles[self.side_colors[1]]):
                        significant_circle = self.get_largest_contour(near_circles[self.side_colors[1]])
                        other_markers = self.get_n_largest_contours(3, near_circles[self.side_colors[0]])
                        s_color = self.side_colors[1]
                        o_color = self.side_colors[0]
                    else:
                        significant_circle = self.get_largest_contour(near_circles[self.side_colors[0]])
                        other_markers = self.get_n_largest_contours(3, near_circles[self.side_colors[1]])
                        s_color = self.side_colors[0]
                        o_color = self.side_colors[1]

                    pos, r = cv2.minEnclosingCircle(significant_circle)
                    # Commented out -> crashes when robot is near edge + slows down vision
                    # pos = Tracker.correct_circle_contour(pos[0], pos[1], pos[0], pos[1], frame,
                    #                                      CORRECTION_STEP, CORRECTION_MAX_DISTANCE,
                    #                                      CORRECTION_AREA_RADIUS, frame[pos[0], pos[1]], 0)
                    markers = [ dict(color=s_color, pos=pos, rad=r) ]

                    for marker in other_markers:
                        pos, r = cv2.minEnclosingCircle(marker)
                        # Commented out -> crashes when robot is near edge + slows down vision
                        # pos = Tracker.correct_circle_contour(pos[0], pos[1], pos[0], pos[1], frame,
                        #                                      CORRECTION_STEP, CORRECTION_MAX_DISTANCE,
                        #                                      CORRECTION_AREA_RADIUS, frame[pos[0], pos[1]], 0)
                        markers.append(dict(color=o_color, pos=pos, rad=r))

                    robot_results.append(TopPlate(dict(pos=cl,color=m_color), markers))

        results = dict(robot_coords=robot_results)
        if self.return_circles:
            results["circles"] = circles
        queue.put(results)


    def update_settings(self):
        for i in range(0, len(self.robots)):
            self.robots[i].present = self.robot_present_vars[i].get()


    def draw_ui(self, parent):
        host = Frame(parent)
        host.pack()

        from os import path
        from PIL import ImageTk, Image
        imgdir = path.join(path.dirname(__file__), "images")

        self.images = list()
        self.robot_present_vars = list()

        for robot in self.robots:
            img = ImageTk.PhotoImage(Image.open(path.join(imgdir, robot.name+".bmp")))

            self.images.append(img)
            self.robot_present_vars.append(BooleanVar(host, robot.present))

            Checkbutton(parent, image=img, variable=self.robot_present_vars[-1],
                        command=self.update_settings).pack(side=LEFT)

            angle_offset_var = UserVariable(parent, float,
                        callback=partial(self.on_angle_offset_changed, robot.name))

            Scale(parent, variable=angle_offset_var, to=50, orient=HORIZONTAL,
                  label="Robot Heading Offset", length=280)

    def on_angle_offset_changed(self, robot, var):
        # TODO
        # print "TODO: change robot angle offset to", var.value
        # robot.offset_angle = var.value? Or is 'robot' only its name?
        pass



