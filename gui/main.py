from common import *

from calibration import CalibrationUI
from tracker_settings import TrackerSettingsUI
from status_control import StatusUI
from gui_settings import GuiSettingsUI

from Tkinter import *
from ttk import *

class MainUI(UserControl):

    def __init__(self, vision_wrapper, master=None):
        UserControl.__init__(self, master, title="Vision Control Panel")
        self.vision = vision_wrapper

        self.tab_host = Notebook(self)

        self.calibrationUI = CalibrationUI(self.vision.calibration, self.tab_host)
        self.tab_host.add(self.calibrationUI, text=self.calibrationUI.title)

        self.trackerUI = TrackerSettingsUI(self.vision.trackers, self.tab_host)
        self.tab_host.add(self.trackerUI, text=self.trackerUI.title)

        self.guiUI = GuiSettingsUI(vision_wrapper, self.tab_host)
        self.tab_host.add(self.guiUI, text=self.guiUI.title)

        self.tab_host.pack()


