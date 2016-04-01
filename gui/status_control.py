# coding=utf-8
from common import *
from PIL import ImageTk, Image

from os import path

class StatusUI(UserControl):

    def __init__(self, vision, parent=None):
        UserControl.__init__(self, parent, title="Vision Status (WIP)")

        self.vision    = vision
        self.user_vars = dict()

        if parent is not None:
            Button(self, text="Detach", command=self.on_detach,
                   padx=2, pady=2, width=8).pack(anchor=NE)
        else:
            Button(self, text="Re-attach", command=self.on_deattach,
                   padx=2, pady=2, width=8).pack(anchor=NE)

        self.frame = Frame(self)
        self.frame.pack(padx=10, pady=10, ipadx=8, ipady=8)

        self.ball_loc_label = Label(self.frame, text = "Ball Location ")
        self.ball_loc_label.pack(padx=15)

        # Vision latency display
        self.latency_label = Label(self.frame, text = "Vision latency ")
        self.latency_label.pack(padx=15)

        self.robot_loc_label = Label(self.frame, text = "Robot Locations ")
        self.robot_loc_label.pack(padx=15)

        self.robot_hed_label = Label(self.frame, text = "Robot Headings ")
        self.robot_hed_label.pack(padx=15)

        self.window.after(300, self.update_vision_values)
        self.window.after(600, self.update_variables)

        StatusUI.instance = self


    def update_vision_values(self, *_):
        if self.vision.target_goal:
            self.target_goal_label.configure(text="Target Goal: %s"%self.vision.target_goal)

        if self.vision.get_ball_position() is None:
            self.ball_loc_label.configure(text="Ball Location: (  NaN,  NaN)")
        else:

            ball_x, ball_y, _ = self.vision.get_ball_position()
            self.ball_loc_label.configure(text="Ball Location: ({:5.2f}, {:5.2f})"
                                      .format(*(ball_x, ball_y)))

        # Display latency
        self.latency_label.configure(text="Vision latency: {:5.3f} ms"
                                     .format(self.vision.get_latency_seconds() * 1000))

        robot_str = "\n".join(("[%s]\t ({:5.2f}, {:5.2f})"%n).format(*p)
                  for (n, p) in self.vision.get_all_robots().items())

        heading_str = "\n".join((u"[{0:s}]\t {{:5.2f}}°".format(n)).format(p)
                    for (n, p) in self.vision.get_robot_headings().items())

        self.robot_loc_label.configure(text="Robot Positions:\n" + robot_str)
        self.robot_hed_label.configure(text="Robot Headings:\n" + heading_str)

        self.window.after(300, self.update_vision_values)


    def on_detach(self):
        self.disintegrate(self.vision)

    def on_deattach(self):
        self.reintegrate(self.vision)

    def _update_label(self, var):
        assert hasattr(var, 'label')
        assert hasattr(var.label, 'base_label')
        var.label['text'] = var.label.base_label + str(var.value)

    def update_variables(self):
        for label in self.user_vars:
            (v1, v2, created) = self.user_vars[label]
            if not created:
                type = v1; initial_value = v2

                var = UserVariable(self, type, initial_value, self._update_label, 200)

                base_label = label + ': '
                lbl = Label(self.frame, text=base_label + str(initial_value))
                lbl.pack(padx=15)
                lbl.base_label = base_label
                var.label = lbl

                self.user_vars[label] = (var, None, True)
        self.window.after(600, self.update_variables)

    @staticmethod
    def add_variable(label, type, initial_value=None):
        if label not in StatusUI.instance.user_vars:
            StatusUI.instance.user_vars[label] = (type, initial_value, False)

    @staticmethod
    def update_variable(label, value):
        if StatusUI.instance.user_vars[label][2]:
            StatusUI.instance.user_vars[label][0].value = value

StatusUI.instance = None
