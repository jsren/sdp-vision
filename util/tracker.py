import numpy as np
import cv2

# Turn off warnings for PolynomialFit
import warnings
warnings.simplefilter('ignore', np.RankWarning)
warnings.simplefilter('ignore', RuntimeWarning)

# Maximum valid contour area contours with a larger area are culled
MAX_CONTOUR_AREA = 50

class Tracker(object):

    @property
    def hasUI(self):
        return False

    def draw_ui(self, parent):
        pass

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

    @staticmethod
    def get_contours(frame, crop, adjustments, is_ball=False):
        """
        Adjust the given frame based on 'min', 'max', 'contrast' and 'blur'
        keys in adjustments dictionary.
        """
        return (list(), None, None)
        try:
            if is_ball:
                frame = frame[crop[2]:crop[3], crop[0]:crop[1]]
            if frame is None:
                return None

            # hp = adjustments['highpass']
            # if hp is None: hp = 0

            if adjustments['contrast'] >= 1.0:
                frame = cv2.add(frame,
                                np.array([float(adjustments['contrast'])]))

            # Convert frame to HSV
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Create a mask
            frame_mask = cv2.inRange(frame_hsv,
                                     np.array(adjustments['min']),
                                     np.array(adjustments['max']))

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

            return ([c for c in contours if cv2.contourArea(c) <= MAX_CONTOUR_AREA],
                    hierarchy, frame_mask)
        except:
            raise


    @staticmethod
    def get_contour_extremes(cnt):
        """
        Get extremes of a countour.
        """
        leftmost   = tuple(cnt[cnt[:, :, 0].argmin()][0])
        rightmost  = tuple(cnt[cnt[:, :, 0].argmax()][0])
        topmost    = tuple(cnt[cnt[:, :, 1].argmin()][0])
        bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])
        return (leftmost, topmost, rightmost, bottommost)


    @staticmethod
    def get_largest_contour(contours):
        """
        Find the largest of all contours.
        """
        areas = [cv2.contourArea(c) for c in contours]
        return contours[np.argmax(areas)]

    @staticmethod
    def get_n_largest_contours(n, contours):
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

    @staticmethod
    def get_contour_centre(contour):
        """
        Find the center of a contour by minimum enclousing circle approximation.

        Returns: ((x, y), radius)
        """
        return cv2.minEnclosingCircle(contour)

    @staticmethod
    def get_angle(line, dot):
        """
        From dot(P2) to line(P1)  [Euclidean]
        """
        diff_x = dot[0] - line[0]
        diff_y = line[1] - dot[1]
        angle = np.arctan2(diff_y, diff_x) * 180 /  np.pi
        return angle



