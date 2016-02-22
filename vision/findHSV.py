import cv2
import numpy as np

'''
findHSV offers a simple calibration tool for calibrating HSV thresholds, contrast, and
blur values for a variety of masks including: red ball, yellow i, blue i, black dot, and
green plate.
Updates to configurations in the GUI result in realtime updates to the masked value making
thresholding very simple.
Attributes:
    CONTROLS    Names the trackbar labels for each trackbar
    MAXBAR      The maximum values for each trackbar
    KEYS        Assigns different colour configurations to keys for quick switching.
'''

CONTROLS = ["LH", "UH", "LS", "US", "LV", "UV", "CT", "BL"]
MAXBAR = {"LH": 360,
          "UH": 360,
          "LS": 255,
          "US": 255,
          "LV": 255,
          "UV": 255,
          "CT": 100,
          "BL": 100
          }

KEYS = {ord('y'): 'yellow',
        ord('r'): 'red',
        ord('b'): 'blue',
        ord('d'): 'dot',
        ord('p'): 'plate',
        ord('i'): 'pink',
        ord('g'): 'green'}

# Used as a empty callback for modifying setting trackbars
def nothing(x):
    pass


class CalibrationGUI(object):
    '''
    CalibrationGUI sets up a simple GUI showing a frame coupled with a series of trackbars 
    offering thresholding of the frame and a mask showing the results.
    '''

    def __init__(self, calibration):
        '''
        Initialises the calibration frame with a new calibration dictionary, to which modifications
        are written as trackbar settings are moved.

        :param calibration: A containing values for each colour, and for each setting.
        '''

        self.color = 'plate'
        self.calibration = calibration
        self.maskWindowName = "Mask " + self.color

        self.setWindow()

    def setWindow(self):
        '''
        Sets up the calibration window with the trackbars assigned to the settings available in calibration 
        dictionary.
        '''

        cv2.namedWindow(self.maskWindowName)

        createTrackbar = lambda setting, value: cv2.createTrackbar(setting, self.maskWindowName, int(value), \
                                                                   MAXBAR[setting], nothing)
        createTrackbar('LH', self.calibration[self.color]['min'][0])
        createTrackbar('UH', self.calibration[self.color]['max'][0])
        createTrackbar('LS', self.calibration[self.color]['min'][1])
        createTrackbar('US', self.calibration[self.color]['max'][1])
        createTrackbar('LV', self.calibration[self.color]['min'][2])
        createTrackbar('UV', self.calibration[self.color]['max'][2])
        createTrackbar('CT', self.calibration[self.color]['contrast'])
        createTrackbar('BL', self.calibration[self.color]['blur'])

    def change_color(self, color):
        '''
        Switches from the previous colour configuration to a new one, displaying the new trackbar values and
        configuration.'''

        cv2.destroyWindow(self.maskWindowName)
        self.color = color
        self.maskWindowName = "Mask " + self.color
        self.setWindow()

    def show(self, frame, key=None):
        '''
        Called whenever a new frame is available, displays the new frame and performs thresholding, displaying 
        the resultant masked image. Also attempts to perform any changes due on the given keypress.

        :param frame: The new image frame to threshold
        :param key: A character keypress code 
        '''

        # Escape key is 255. If not, attempt to change colour - will throw an exception if not found in the
        # dictionary.
        if key != 255:
            try:
                self.change_color(KEYS[key])
            except:
                pass

        # Construct a convenience function for retrieving trackbar position for each control
        getTrackbarPos = lambda setting: cv2.getTrackbarPos(setting, self.maskWindowName)

        # Read in all the trackbar values
        values = {}
        for setting in CONTROLS:
            values[setting] = float(getTrackbarPos(setting))
        values['BL'] = int(values['BL'])

        # Assign all the new calibration values
        self.calibration[self.color]['min'] = np.array([values['LH'], values['LS'], values['LV']])
        self.calibration[self.color]['max'] = np.array([values['UH'], values['US'], values['UV']])
        self.calibration[self.color]['contrast'] = values['CT']
        self.calibration[self.color]['blur'] = values['BL']

        # Mask the new frame using values and display
        mask = self.get_mask(frame)
        cv2.imshow(self.maskWindowName, mask)

    def get_mask(self, frame):
        '''
        Applies the given contrast / blur preprocessing steps to the frame and then thresholds
        using our HSV settings. 

        :param frame: A frame to preprocess and threshold 
        :returns: A masked frame, masked using our settings with preprocessing applied.
        '''

        # Apply basic blur to the image
        blur = self.calibration[self.color]['blur']
        if blur > 1:
            frame = cv2.blur(frame, (blur, blur))

        # Alter contrast
        contrast = self.calibration[self.color]['contrast']
        if contrast > 1.0:
            frame = cv2.add(frame, np.array([contrast]))

        # Apply HSV thresholding using our settings
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        min_color = self.calibration[self.color]['min']
        max_color = self.calibration[self.color]['max']

        frame_mask = cv2.inRange(frame_hsv, min_color, max_color)

        return frame_mask

    @staticmethod
    def highpass(frame_mask, frame, hp):
        hp = int(hp)

        if hp >= 1:
            blur = 10
            if blur % 2 == 0:
                blur += 1
            f2 = cv2.GaussianBlur(frame, (blur, blur), 0)

            lap = cv2.Laplacian(f2, ddepth=cv2.CV_16S, ksize=5, scale=1)
            lap = cv2.convertScaleAbs(lap)

            blur = 5
            if blur % 2 == 0:
                blur += 1
            lap = cv2.GaussianBlur(lap, (blur, blur), 0)

            frame_hsv = cv2.cvtColor(lap, cv2.COLOR_BGR2HSV)

            frame_mask_lap = cv2.inRange(frame_hsv, np.array([0, 0, hp]), np.array([360, 255, 255]))
            f_mask = cv2.bitwise_and(frame_mask, frame_mask_lap)

            return f_mask

        return frame_mask
