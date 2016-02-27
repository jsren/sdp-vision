import numpy as np
from numpy import dot


class Kalman:
    # Timestep in between frames
    dt = 0.0416

    # Matrices:

    '''
    Produces transition to next state.
    Matrix A.
    
    x = x + dx
    y = y + dy
    dx = dx
    dy = dy
    '''
    TransitionMatrix = np.array([[1, 0, 1, 0],
                                 [0, 1, 0, 1],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]])

    '''
    Will not be used but it accounts for the
    control vector things such as acceleration etc.
    Matrix B.
    '''
    InputControl = np.array([[1, 0, 0, 0],
                             [0, 1, 0, 0],
                             [0, 0, 1, 0],
                             [0, 0, 0, 1]])

    '''
    Converts state transitions back to measurements
    A pointless computation in this case.
    Matrix H.
    '''
    MeasurementMatrix = np.array([[1, 0, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])

    '''
    Covariance Matrix for the measurements
    quantifies the error in the state transition.
    Matrix Q.
    '''
    ActionUncertainty = np.array([[0, 0, 0,   0],
                                  [0, 0, 0,   0],
                                  [0, 0, 0.1, 0],
                                  [0, 0, 0, 0.1]])

    '''
    Covariance matrix for uncertainty in measurements.
    Matrix R.
    '''
    SensorUncertainty = np.array([[0.1, 0, 0, 0],
                                  [0, 0.1, 0, 0],
                                  [0, 0, 0.1, 0],
                                  [0, 0, 0, 0.1]])

    #  Estimated coovariance for Kalman gain
    P = np.zeros((4, 4))

    # Identity Matrix
    I = np.identity(4)

    # Vectors: 
    control_vector = np.array([0, 0, 0, 0])  # Vector with u's
    prediction = np.array([0, 0, 0, 0])  # Vector with x's

    def __init__(self,
                 TransitionMatrix=TransitionMatrix,
                 InputControl=InputControl,
                 MeasurementMatrix=MeasurementMatrix,
                 ActionUncertainty=ActionUncertainty,
                 SensorUncertainty=SensorUncertainty,
                 control_vector=control_vector):
        """
        Constructor for Kalman filter object sets up Matrices for
        state changes and evaluations before hand yet allows them
        to be passed as parameters
        """
        self.InputControl = InputControl
        self.MeasurementMatrix = MeasurementMatrix
        self.ActionUncertainty = ActionUncertainty
        self.SensorUncertainty = SensorUncertainty


    def estimate(self, measurement_vec):
        """
        Calls the prediction step and correction step on the given measurement vector.
        """
        return self.correction_step(self.prediction_step(measurement_vec))

    def prediction_step(self, measurement_vec):
        """
        Carries out the measurement step for given measurements and returns a prediction.
        """
        measurement_vec = np.array(measurement_vec)

        # Transitioning to the next state
        self.prediction = dot(self.TransitionMatrix, measurement_vec) + \
            dot(self.InputControl, self.control_vector)
        
        # Evaluating a priori estimate error covariance
        self.P = dot(self.TransitionMatrix, dot(self.P, self.TransitionMatrix.T)) + \
            self.ActionUncertainty
        
        # print self.prediction
        return self.prediction


    def correction_step(self, measurement_vec):
        """
        Carries out the correction step for given measurements and returns the corrected predictions.
        """        
        # Compute Kalman Gain K
        S = dot(self.MeasurementMatrix, dot(self.P, self.MeasurementMatrix.T)) + \
            self.SensorUncertainty
        S_inv = np.linalg.inv(S)
        K = dot(self.P, dot(self.MeasurementMatrix.T, S_inv))

        # Updte estimates
        y = measurement_vec - dot(self.MeasurementMatrix, self.prediction)
        self.prediction = self.prediction + dot(K, y)

        # Update the error covariance P
        self.P = dot((self.I - dot(K, self.MeasurementMatrix)), self.P)
        
        return self.prediction


    def n_frames(self, n, measurement_vec):
        """
        Predicts n steps in advance.
        """
        for i in xrange(n):
            measurement_vec = self.estimate(measurement_vec)
        return measurement_vec


if __name__ == '__main__':
    a = Kalman()
    vector = [1,1,20,20]
    print a.P
    print a.n_frames(0,vector)
    print a.P