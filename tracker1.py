from collections import namedtuple
from scipy.cluster.vq import kmeans
from util import RobotInstance

import numpy as np
import cv2


# Turn off warnings for PolynomialFit
import warnings
warnings.simplefilter('ignore', np.RankWarning)
warnings.simplefilter('ignore', RuntimeWarning)


BoundingBox = namedtuple('BoundingBox', 'x y width height')
Center = namedtuple('Center', 'x y')

NUMBER_OF_MAIN_CIRCLES_PER_COLOR = 2
NUMBER_OF_SIDE_CIRCLES_PER_COLOR = 16

ROBOT_DISTANCE = 20


class Tracker(object):

    @staticmethod
    def oddify(inte):
        """
        :param inte: number
        :return: same number, if it's odd, number-1 if even, 1 if number is 0.
        """
        if inte == 0:
            inte += 1
        elif inte % 2 == 0:
            inte -= 1
        else:
            pass
        return inte

    def get_contours(self, frame, crop, adjustments, o_type=None):
        """
        Adjust the given frame based on 'min', 'max', 'contrast' and 'blur'
        keys in adjustments dictionary.
        """
        try:

            if o_type == 'BALL':
                frame = frame[crop[2]:crop[3], crop[0]:crop[1]]
            if frame is None:
                return None



            hp = adjustments.get('highpass')

            if hp is None:
                hp = 0

            if adjustments['contrast'] >= 1.0:
                frame = cv2.add(frame,
                                np.array([float(adjustments['contrast'])]))

            # Convert frame to HSV
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Create a mask

            frame_mask = cv2.inRange(frame_hsv,
                                     adjustments['min'],
                                     adjustments['max'])



            # Does nothing since highpass is 0.0 everywhere in calibrations.json
            # frame_mask = CalibrationGUI.highpass(frame_mask, frame, hp)

            # Find contours
            if adjustments['open'] >= 1:
                kernel = np.ones((2,2),np.uint8)
                frame_mask = cv2.morphologyEx(frame_mask,
                                              cv2.MORPH_OPEN,
                                              kernel,
                                              iterations=adjustments['open'])

            if adjustments['close'] >= 1:
                kernel = np.ones((2,2),np.uint8)
                frame_mask = cv2.dilate(frame_mask,
                                        kernel,
                                        iterations=adjustments['close'])

            if adjustments['erode'] >= 1:
                kernel = np.ones((2,2),np.uint8)
                frame_mask = cv2.erode(frame_mask,
                                        kernel,
                                        iterations=adjustments['erode'])






            tmp_placeholder, contours, hierarchy = cv2.findContours(
                frame_mask,
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )

            return (contours, hierarchy, frame_mask)
        except:
            # bbbbb
            raise


    def get_contour_extremes(self, cnt):
        """
        Get extremes of a countour.
        """
        leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
        rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
        topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
        bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])
        return (leftmost,
                topmost,
                rightmost,
                bottommost)

    '''
    def get_bounding_box(self, points):
        """
        Find the bounding box given points by looking at the extremes of each coordinate.
        """
        leftmost = min(points, key=lambda x: x[0])[0]
        rightmost = max(points, key=lambda x: x[0])[0]
        topmost = min(points, key=lambda x: x[1])[1]
        bottommost = max(points, key=lambda x: x[1])[1]
        return BoundingBox(leftmost,
                           topmost,
                           rightmost - leftmost,
                           bottommost - topmost)

    def get_contour_corners(self, contour):
        """
        Get exact corner points for the plate given one contour.
        """
        if contour is not None:
            rectangle = cv2.minAreaRect(contour)
            box = cv2.cv.BoxPoints(rectangle)
            return np.int0(box)
    def join_contours(self, contours):
        """
        Joins multiple contours together.
        """
        cnts = []
        for i, cnt in enumerate(contours):
            if cv2.contourArea(cnt) > 100:
                cnts.append(cnt)
        return reduce(lambda x, y: np.concatenate((x, y)),
                                   cnts) if len(cnts) else None
    '''

    def get_largest_contour(self, contours):
        """
        Find the largest of all contours.
        """
        areas = [cv2.contourArea(c) for c in contours]
        return contours[np.argmax(areas)]

    def get_n_largest_contours(self, n, contours):
        """
        Return a numpy array of n largest contours, or less if the array is smaller
        """
        contours = np.array(contours)
        areas = [cv2.contourArea(c) for c in contours]
        return contours[np.array(areas).argsort()[::-1][:n]]

    '''
    def get_smallest_contour(self, contours):
        """
        Find the smallest of all contours.
        """
        areas = [cv2.contourArea(c) for c in contours]
        ind = np.argsort(areas)
        # for i in range(len(ind)):
        #     if areas[ind[i]] > 5:
        #         return areas[ind[i]]
        return contours[np.argmin(areas)]
    '''

    def get_contour_centre(self, contour):
        """
        Find the center of a contour by minimum enclousing circle approximation.

        Returns: ((x, y), radius)
        """
        return cv2.minEnclosingCircle(contour)

    def get_angle(self, line, dot):
        """
        From dot(P2) to line(P1)  [Euclidean]
        """
        diff_x = dot[0] - line[0]
        diff_y = line[1] - dot[1]
        angle = np.arctan2(diff_y, diff_x) * 180 /  np.pi
        return angle


class CircleTracker(Tracker):
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

        self.main_colors = main_colors
        self.side_colors = side_colors
        self.colors = main_colors + side_colors
        self.crop = crop
        self.pitch = pitch
        self.calibration = calibration
        self.return_circles = return_circles
        self.robots = []


    def find_all_circles(self, frame):
        """
        Returns all colored circles found. Colors are set in calibrations.json
        :param frame:   Current camera frame
        :return:        {color:[circles]}
        """
        circles = dict()
        for color in set(self.colors):
            # Get all circles of the given colour
            contours, hierarchy, mask = self.get_contours(frame.copy(), self.crop, self.calibration[color], '')

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


class BallTracker(Tracker):
    """
    Track red ball on the pitch.
    """

    def __init__(self,
                 crop,
                 offset,
                 pitch,
                 calibration,
                 name='ball'):
        """
        Initialize tracker.

        Params:
            [string] color      the name of the color to pass in
            [(left-min, right-max, top-min, bot-max)]
                                crop  crop coordinates
            [int] offset        how much to offset the coordinates
        """
        self.crop = crop
        # if pitch == 0:
        #     self.color = PITCH0['red']
        # else:
        #     self.color = PITCH1['red']
        self.color = [calibration['red']]
        self.offset = offset
        self.name = name
        self.calibration = calibration

    def find(self, frame, queue):
        for color in self.color:
            """
            contours, hierarchy, mask = self.preprocess(
                frame,
                self.crop,
                color['min'],
                color['max'],
                color['contrast'],
                color['blur']
            )
            """
            # adjustments = {'min':,'mz'}
            contours, hierarchy, mask = self.get_contours(frame.copy(),
                                                          self.crop,
                                                          color,
                                                          'BALL')

            if len(contours) <= 0:
                #print 'No ball found.'
                pass
                # queue.put(None)
            else:
                # Trim contours matrix
                cnt = self.get_largest_contour(contours)

                # Get center
                (x, y), radius = cv2.minEnclosingCircle(cnt)

                queue.put({
                    'name': self.name,
                    'x': x,
                    'y': y,
                    'angle': None,
                    'velocity': None
                })
        queue.put(None)
        pass
