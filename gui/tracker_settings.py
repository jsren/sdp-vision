from common import *

class TrackerSettingsUI(UserControl):

    def __init__(self, trackers, parent=None):
        UserControl.__init__(self, parent, "Tracker Settings")

        for tracker in trackers:
            if not tracker.hasUI: continue

            frame = LabelFrame(self, text=tracker.__class__.__name__.title() + " Settings")
            frame.pack(padx=10, pady=10, ipadx=8, ipady=8)
            try:
                tracker.draw_ui(frame)
            except Exception, e:
                print "[ERROR] [UI]", e

    @staticmethod
    def create_and_show(trackers, parent=None):
        TrackerSettingsUI(trackers, parent).show()

if __name__ == "__main__":
    TrackerSettingsUI.create_and_show(list())