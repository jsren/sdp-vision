from common import *
from Tkinter import *
from config import Configuration

from functools import partial


class GuiSettingsUI(UserControl):

    def __init__(self, vision_wrapper, master=None):
        UserControl.__init__(self, master, title="GUI Settings")
        self.vision = vision_wrapper

        self.show_contours_var = UserVariable(self, int, True, self.on_show_contours_changed, 500)
        self.show_ball_var = UserVariable(self, int, True, self.on_show_ball_changed, 500)
        self.show_ballv_var = UserVariable(self, int, True, self.on_show_ballv_changed, 500)
        self.show_robots_var = UserVariable(self, int, True, self.on_show_robots_changed, 500)

        Checkbutton(self, text="Show Ball", variable=self.show_ball_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(self, text="Show Velocity", variable=self.show_ballv_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(self, text="Show Robots", variable=self.show_robots_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(self, text="Show Contours", variable=self.show_contours_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)

        self.selector_frame = LabelFrame(self, text="Camera Settings")
        self.selector_frame.grid(row=0, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self._vars = list()

        max_values = Configuration.video_settings_max['big'] \
                        if self.vision.color_settings in [0, "small"] \
                        else Configuration.video_settings_max['small']


        for att in self.vision.video_settings:
            var = UserVariable(self, float, 0, partial(self.on_video_att_changed, att), 500)
            self._vars.append(var)

            Scale(self.selector_frame, variable=var, to=max_values[att],
                  orient=HORIZONTAL, label=att.title(), length=300).pack(anchor=W, padx=5, pady=5)


        self.button_frame = Frame(self)
        self.button_frame.grid(row=1, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        Button(self.button_frame, text="Write Video Settings", command=self.commit_settings,
               padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Reload from File", command=self.reload_config,
                padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Quit", command=self.close,
                padx=10, pady=10, width=15).pack(side=RIGHT)

    def on_show_contours_changed(self, var):
        self.vision.gui.draw_contours = bool(var.value)

    def on_show_ball_changed(self, var):
        self.vision.gui.draw_ball = bool(var.value)

    def on_show_ballv_changed(self, var):
        self.vision.gui.draw_ball_velocity = bool(var.value)

    def on_show_robots_changed(self, var):
        self.vision.gui.draw_robots = bool(var.value)

    def on_video_att_changed(self, att, var):
        self.vision.video_settings[att] = var.value

    def reload_config(self):
        video_settings = Configuration.read_video_config(
            self.vision.video_settings.machine_name)

        for setting in video_settings:
            self.config[setting] = video_settings[setting]

        self.vision.video_settings.commit()
        pass

    def commit_settings(self):
        i = 0
        for att in self.vision.video_settings:
            self.config[att] = self._vars[i]
            i += 1

        Configuration.write_video_config(self.config,
                                         self.vision.video_settings.machine_name)

