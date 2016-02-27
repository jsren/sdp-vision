from util import Tracker, RobotInstance

from scipy.cluster.vq import kmeans

import cv2
import numpy as np


NUMBER_OF_MAIN_CIRCLES_PER_COLOR = 2
NUMBER_OF_SIDE_CIRCLES_PER_COLOR = 16

ROBOT_DISTANCE = 20



class RobotTracker(Tracker):
    def __init__(self,
                 main_colors,
                 side_colors,
                 crop,
                 pitch,
                 calibration,
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
        self.robots         = []


    def find_all_circles(self, frame):
        """
        Returns all colored circles found. Colors are set in calibrations.json
        :param frame:   Current camera frame
        :return:        {color:[circles]}
        """
        circles = dict()
        for color in set(self.colors):
            # Get all circles of the given colour
            contours, hierarchy, mask = self.get_contours(frame.copy(), self.crop,
                    self.calibration.get_color_setting(self.pitch, self.colors), '')

            circles[color] = contours

            # Get only the required number of colors.
            if color in self.main_colors:
                circles[color] = self.get_n_largest_contours(
                    NUMBER_OF_MAIN_CIRCLES_PER_COLOR, circles[color])

            elif color in self.side_colors:
                circles[color] = self.get_n_largest_contours(
                    NUMBER_OF_SIDE_CIRCLES_PER_COLOR, circles[color])

        return circles


    def initialize_robots(self, frame):
        circles = self.find_all_circles(frame)

        clusters = []
        # Use k-means to find cluster centres for main colors
        for m_color in self.main_colors:

            cls = self.find_color_clusters(circles[m_color], 1)
            if cls.any() and len(cls) == 1: # and np.linalg.norm(cls[0] - cls[1]) > 20:
                cls.append(m_color)
                clusters.append(cls)

        for c in xrange(len(clusters)):
            x = clusters[c][0]
            y = clusters[c][1]
            m_color = clusters[c][2]
            self.robots[c] = RobotInstance(x, y, m_color)





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
            (x, y), radius = cv2.minEnclosingCircle(crc)
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
        circle_results = []
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

                            d2 = ((x0-cl[0])**2 + (y0-cl[1])**2)
                            # if d2 < 50 ** 2:
                            #     print "[INFO] Circle distances: " + str(d2**0.5), color
                            if (x0-cl[0])**2 + (y0-cl[1])**2 < ROBOT_DISTANCE**2:
                                near_circles[color].append(circle)


                    # Find the significant side circle
                    if len(near_circles[self.side_colors[0]]) == 0 or len(near_circles[self.side_colors[1]]) == 0:
                        continue
                    if len(near_circles[self.side_colors[0]]) > len(near_circles[self.side_colors[1]]):
                        significant_circle = self.get_largest_contour(near_circles[self.side_colors[1]])
                        s_color = self.side_colors[1]
                    else:
                        significant_circle = self.get_largest_contour(near_circles[self.side_colors[0]])
                        s_color = self.side_colors[0]

                    (x, y), radius = cv2.minEnclosingCircle(significant_circle)
                    circle_results.append({'clx': cl[0], 'cly': cl[1], 'x': x, 'y':y, 'main_color': m_color, 'side_color': s_color})

        results = dict(robot_coords=circle_results)
        if self.return_circles:
            results["circles"] = circles
        queue.put(results)


        # 1) returns the most relevant circles found.
        # queue.put({
        #     "circles":circles
        # })
