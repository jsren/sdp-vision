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
        self.show_raw_var = UserVariable(self, int, False, self.on_show_raw_changed, 500)

        opts_frame = LabelFrame(self, text="Video Feed Ooptions")
        opts_frame.pack()

        Checkbutton(opts_frame, text="Show Ball", variable=self.show_ball_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(opts_frame, text="Show Velocity", variable=self.show_ballv_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(opts_frame, text="Show Robots", variable=self.show_robots_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(opts_frame, text="Show Contours", variable=self.show_contours_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(opts_frame, text="Enable Raw Video", variable=self.show_raw_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)

        self.selector_frame = LabelFrame(self, text="Camera Settings")
        self.selector_frame.pack(padx=5, ipadx=5, pady=5, ipady=5)

        self._vars = list()

        max_values = Configuration.video_settings_max['small'] \
                        if self.vision.color_settings in [0, "small"] \
                        else Configuration.video_settings_max['big']


        for att in self.vision.video_settings:
            if att not in max_values: continue

            var = UserVariable(self, int, 0, partial(self.on_video_att_changed, att), 500)
            var.attribute = att
            self._vars.append(var)

            Scale(self.selector_frame, variable=var, to=max_values[att],
                  orient=HORIZONTAL, label=att.title(), length=300).pack(anchor=W, padx=5, pady=5)


        self.button_frame = Frame(self)
        self.button_frame.pack(padx=5, ipadx=5, pady=5, ipady=5)

        Button(self.button_frame, text="Write Video Settings", command=self.commit_settings,
               padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Reload from File", command=self.reload_config,
                padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Quit", command=self.close,
                padx=10, pady=10, width=15).pack(side=RIGHT)

        self.reload_config()



    def on_show_contours_changed(self, var):
        self.vision.gui.draw_contours = bool(var.value)

    def on_show_ball_changed(self, var):
        self.vision.gui.draw_ball = bool(var.value)

    def on_show_ballv_changed(self, var):
        self.vision.gui.draw_ball_velocity = bool(var.value)

    def on_show_robots_changed(self, var):
        self.vision.gui.draw_robots = bool(var.value)

    def on_show_raw_changed(self, var):
        self.vision.camera.raw_output_mode = bool(var.value)


    def on_video_att_changed(self, att, var):
        self.vision.video_settings[att] = var.value
        self.vision.video_settings.commit()

    def reload_config(self):
        video_settings = Configuration.read_video_config(
            self.vision.video_settings.machine_name)

        for var in self._vars:
            var.value = video_settings[var.attribute]


    def commit_settings(self):
        for var in self._vars:
            self.vision.video_settings[var.attribute] = var.value

        Configuration.write_video_config(self.vision.video_settings,
                                         self.vision.video_settings.machine_name)
