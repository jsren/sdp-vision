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
