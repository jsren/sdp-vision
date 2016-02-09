from vision.vision import Vision, Camera
import vision.tools as tools
from postprocessing import Postprocessing
from preprocessing.preprocessing import Preprocessing
import cv2
from copy import deepcopy

class VisionWrapper:
    """
    Class that handles vision

    """

    def __init__(self, pitch, color, our_side, video_port=0):
        """
        Entry point for the SDP system.

        Params:
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] colour                 The colour of our teams plates
            [string] our_side               the side we're on - 'left' or 'right'
            [int] video_port                port number for the camera
        Fields
            pitch
            camera
            calibration
            vision
            postporcessing
            color
            side
            preprocessing
            model_positions
            regular_positions
        """
        assert pitch in [0, 1]
        assert color in ['yellow', 'blue']
        assert our_side in ['left', 'right']

        self.pitch = pitch

        # Set up camera for frames
        self.camera = Camera(port=video_port, pitch=pitch)
        self.camera.start_capture()
        self.frame = self.camera.get_frame()
        center_point = self.camera.get_adjusted_center(self.frame)

        # Set up vision
        self.calibration = tools.get_colors(pitch)
        self.vision = Vision(
            pitch=pitch, color=color, our_side=our_side,
            frame_shape=self.frame.shape, frame_center=center_point,
            calibration=self.calibration)

        # Set up preprocessing and postprocessing
       # self.postprocessing = Postprocessing()
        self.preprocessing = Preprocessing()

        self.color = color
        self.side = our_side

        self.frameQueue = []


    def update(self):
        """
        Gets this frame's positions from the vision system.
        """

        self.frame = self.camera.get_frame()

        # Apply preprocessing methods toggled in the UI
        self.preprocessed = self.preprocessing.run(self.frame, self.preprocessing.options)
        self.frame = self.preprocessed['frame']
        if 'background_sub' in self.preprocessed:
            cv2.imshow('bg sub', self.preprocessed['background_sub'])

        # Find object positions
        # model_positions have their y coordinate inverted
        self.model_positions, self.regular_positions = self.vision.locate(self.frame)
        #self.model_positions = self.postprocessing.analyze(self.model_positions)

        #self.model_positions = self.averagePositions(3, self.model_positions)

    def averagePositions(self, frames, positions_in):
        """
        :param frames: number of frames to average
        :param positions_in: positions for the current frame
        :return: averaged positions
        """

        validFrames = self.frameQueue.__len__() + 1

        positions_out = deepcopy(positions_in)
        # Check that the incoming positions have legal values
        for obj in positions_out.items():
            if (positions_out[obj[0]].velocity is None):
                positions_out[obj[0]].velocity = 0
            if positions_out[obj[0]].x is None:
                positions_out[obj[0]].x = 0
            if positions_out[obj[0]].y is None:
                positions_out[obj[0]].y = 0
            positions_out[obj[0]].angle = positions_in[obj[0]].angle

        # Loop over queue
        for positions in self.frameQueue:
            # Loop over each object in the position dictionary
            isFrameValid = True
            for obj in positions.items():
                # Check if the current object's positions have legal values
                if (obj[1].x is None) or (obj[1].y is None) or (obj[1].angle is None) or (obj[1].velocity is None):
                    isFrameValid = False
                else:
                    positions_out[obj[0]].x += obj[1].x
                    positions_out[obj[0]].y += obj[1].y
                    positions_out[obj[0]].velocity += obj[1].velocity

            if not isFrameValid and validFrames > 1:
                #validFrames -= 1
                pass

        # Loop over each object in the position dictionary and average the values
        for obj in positions_out.items():
            positions_out[obj[0]].velocity /= validFrames
            positions_out[obj[0]].x /= validFrames
            positions_out[obj[0]].y /= validFrames


        # If frameQueue is already full then pop the top entry off
        if self.frameQueue.__len__() >= frames:
            self.frameQueue.pop(0)

        # Add our new positions to the end
        self.frameQueue.append(positions_in)

        return positions_out


    def saveCalibrations(self):
        tools.save_colors(self.vision.pitch, self.calibration)


'''
vision = VisionWrapper(0, "blue", "left", 0)
while True:
    vision.update()  # get the new frame
    frame0 = vision.frame  # use that new frame

    # Display the resulting frame
    cv2.imshow('frame', frame0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vision.camera.stop_capture()
cv2.destroyAllWindows()
'''