from util import Tracker, RobotInstance

from scipy.cluster.vq import kmeans
from Tkinter import *

import cv2
import numpy as np


NUMBER_OF_MAIN_CIRCLES_PER_COLOR = 2
NUMBER_OF_SIDE_CIRCLES_PER_COLOR = 16

ROBOT_DISTANCE = 30



class RobotTracker(Tracker):

    @property
    def hasUI(self):
        return True

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
            contours, hierarchy, mask = self.get_contours(frame, self.crop,
                   cal)

            if color in self.main_colors:
                circles[color] = self.get_n_largest_contours2(
                    NUMBER_OF_SIDE_CIRCLES_PER_COLOR*2, contours)

            elif color in self.side_colors:
                circles[color] = self.get_n_largest_contours2(
                    NUMBER_OF_SIDE_CIRCLES_PER_COLOR*2, contours)

            else: raise Exception("Invalid colour")

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

    def find_color_clusters2(self, circles_of_one_color, k, iter=20):
        """
        Returns k cluster centres of one color
        :param frame:   Current camera frame
        :param circles: [circles]
        :param k:       int, number of cluster centres
        :param iter:    int, number of times to iterate k-means
        :return:    [[(x,y)]] - coordinates of found centres
        """
        points = np.array([c[0] for c in circles_of_one_color])
        try:
            return kmeans(points, k, iter=iter)[0]
        except ValueError:
            return np.array([])


    def find(self, frame, queue):

        # results = dict(robot_coords=dict())
        # if self.return_circles:
        #      results["circles"] = dict()
        # #queue.put(results)
        # return results

        # Array of contours found.
        circles_by_color = self.find_all_circles(frame)

        # Use k-means to find cluster centres for main colors
        circle_results = []
        #
        # circles = { color:
        #             for color in circles_by_color}

        nearby = dict().fromkeys(circles_by_color.keys(), list())

        for color in circles_by_color:
            circs2 = list(circles_by_color[color])

            while len(circs2) > 0:
                c = circs2.pop()
                count = len([d for d in [(c[0][0] - c1[0][0])**2 + (c[0][1] - c1[0][1])**2 for c1 in circs2]
                                   if d < ROBOT_DISTANCE**2])
                if count >= 7:
                    nearby[color].append(c)

        circle_results = list()

        clusters = dict()
        for color in ['yellow', 'blue']:
            clusters[color] = self.find_color_clusters2(nearby[color], 2)


        for color in ['yellow', 'blue']:
            for point in clusters[color]:
                for color2 in ['green', 'pink']:
                    for p2 in nearby[color2]:
                        if (p2[0][0]-point[0])**2 + (p2[0][1]-point[1])**2 < ROBOT_DISTANCE**2:
                            circle_results.append({'clx': point[0], 'cly': point[1], 'x': p2[0][0], 'y': p2[0][1],
                                                   'main_color': color, 'side_color': color2})


        # for color in circles_by_color:
        #     circles[] = self.find_color_clusters2(circles_by_color[m_color], 2)
        #
        # for m_color in self.main_colors:
        #
        #     circles[] = self.find_color_clusters2(circles_by_color[m_color], 2)
        #     if (len(cls) >= 2 and np.linalg.norm(cls[0] - cls[1]) > ROBOT_DISTANCE)\
        #                  or any([abs(cls[1]-2) < 0.5]):
        #
        #         # For each cluster, find near circles
        #         for cl in cls:
        #             near_circles = { k : [] for k in self.side_colors }
        #
        #             for (color, subcircs) in circles_by_color.iteritems():
        #                 if color not in self.side_colors: continue
        #
        #                 for circle in subcircs:
        #                     if (circle[0][0]-cl[0])**2 + (circle[0][1]-cl[1])**2 < ROBOT_DISTANCE**2:
        #                         near_circles[color].append(circle)
        #
        #
        #             # Find the significant side circle
        #             if len(near_circles[self.side_colors[0]]) == 0 or \
        #                             len(near_circles[self.side_colors[1]]) == 0:
        #                 continue
        #             if len(near_circles[self.side_colors[0]]) > len(near_circles[self.side_colors[1]]):
        #                 significant_circle = self.get_largest_contour(near_circles[self.side_colors[1]])
        #                 s_color = self.side_colors[1]
        #             else:
        #                 significant_circle = self.get_largest_contour(near_circles[self.side_colors[0]])
        #                 s_color = self.side_colors[0]
        #
        #             (x, y), _ = cv2.minEnclosingCircle(significant_circle)
        #             circle_results.append({'clx': cl[0], 'cly': cl[1], 'x': x, 'y': y, 'main_color': m_color, 'side_color': s_color})

        results = dict(robot_coords=circle_results)
        if self.return_circles:
             results["circles"] = nearby
        #queue.put(results)
        return results

        # 1) returns the most relevant circles found.
        # queue.put({
        #     "circles": circles_by_color
        # })

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



