from util import Tracker

import cv2


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
        self.crop   = crop
        self.color  = calibration['red']
        self.offset = offset
        self.name   = name

    def find(self, frame, queue):
        #for color in self.color:
        if True:
            """
            contours, hierarchy, mask = self.preprocess(
                frame,
                self.crop,
                color['min'],
                color['max'],            # adjustments = {'min':,'mz'}

            adjustments = calibration[color]
                color['contrast'],
                color['blur']
            )
            """

            contours, hierarchy, mask = self.get_contours(frame.copy(),
                                                          self.crop,
                                                          self.color,
                                                          True)
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
                    'velocity': None,
                    'ball_contour': cnt
                })
        queue.put(None)
        pass
