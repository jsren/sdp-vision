from common import *

class TrackerSettingsUI(UserControl):

    def __init__(self, trackers, parent=None):
        UserControl.__init__(self, parent, "Tracker Settings")

        self.trackers = trackers

        row = 0
        for tracker in trackers:
            if not tracker.hasUI: continue

            frame = LabelFrame(self, text=tracker.__name__.title() + " Settings")
            frame.grid(row=row, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)
            row += 1
            try:
                tracker.draw_ui(frame)
            except Exception, e:
                print e


    @staticmethod
    def create_and_show(trackers, parent=None):
        TrackerSettingsUI(trackers).show()

