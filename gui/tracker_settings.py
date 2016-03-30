from common import *

import util.robot_instance

class TrackerSettingsUI(UserControl):

    def __init__(self, trackers, parent=None):
        UserControl.__init__(self, parent, "Tracker Settings")

        # Store for disintegrate
        self._trackers = trackers

        if parent is not None:
            Button(self, text="Detach", command=self.on_detach,
                   padx=2, pady=2, width=8).pack(anchor=NE)
        else:
            Button(self, text="Re-attach", command=self.on_deattach,
                   padx=2, pady=2, width=8).pack(anchor=NE)

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

        radjust_var = UserVariable(self, int, int(util.robot_instance.marker_angle_offset),
                                   self.on_radjust_changed)

        Scale(frame, variable=radjust_var, from_=-180, to=180, orient=HORIZONTAL,
              label="Robot Orientation Adjustment", length=300)\
            .pack(anchor=W, padx=5, pady=5)


    def on_radjust_changed(self, var):
        util.robot_instance.marker_angle_offset = var.value

    def on_detach(self):
        self.disintegrate(self._trackers)

    def on_deattach(self):
        self.reintegrate(self._trackers)

    @staticmethod
    def create_and_show(trackers, parent=None):
        TrackerSettingsUI(trackers, parent).show()


if __name__ == "__main__":
    TrackerSettingsUI.create_and_show(list())

