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

        frame = LabelFrame(self, text="Manual Adjustment")
        frame.pack(padx=10, pady=10, ipadx=8, ipady=8)

        radjust_var = UserVariable(self, int, 0, self.on_radjust_changed)

        Scale(frame, variable=radjust_var, from_=-180, to=180, orient=HORIZONTAL,
              label="Robot Orientation Adjustment", length=300)\
            .pack(anchor=W, padx=5, pady=5)


    def on_radjust_changed(self, var):
        print "[INFO] Angle adjust changed to", var.value

    @staticmethod
    def create_and_show(trackers, parent=None):
        TrackerSettingsUI(trackers, parent).show()


if __name__ == "__main__":
    TrackerSettingsUI.create_and_show(list())
