#import sys, os.path as _path
#sys.path.append(_path.join(_path.dirname(__file__), "../"))

from vision import Camera
import cv2
from matplotlib import pyplot as plt



cam = Camera(0)
cam.start_capture()
frame = cam.get_frame()
cam.stop_capture()

cam.fix_radial_distortion(frame)

# hist
hist = cv2.calcHist([frame],[0],None,[256],[0,256])
plt.subplot(221), plt.imshow(hist, 'gray')
plt.xlim([0,256])
plt.show()