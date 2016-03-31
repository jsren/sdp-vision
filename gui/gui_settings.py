from common import *
from Tkinter import *
from ..config import Configuration

from functools import partial


class GuiSettingsUI(UserControl):

    def __init__(self, vision_wrapper, parent=None):
        UserControl.__init__(self, parent, title="GUI Settings")
        self.vision = vision_wrapper

        if parent is not None:
            Button(self, text="Detach", command=self.on_detach,
                   padx=2, pady=2, width=8).pack(anchor=NE)
        else:
            Button(self, text="Re-attach", command=self.on_deattach,
                   padx=2, pady=2, width=8).pack(anchor=NE)

        self.show_contours_var = UserVariable(self, int, True, self.on_show_contours_changed, 500)
        self.show_ball_var = UserVariable(self, int, True, self.on_show_ball_changed, 500)
        self.show_ballv_var = UserVariable(self, int, True, self.on_show_ballv_changed, 500)
        self.show_robots_var = UserVariable(self, int, True, self.on_show_robots_changed, 500)
        self.show_correct_var = UserVariable(self, int, False, self.on_show_correct_changed, 500)
        self.show_raw_var = UserVariable(self, int, False, self.on_show_raw_changed, 500)

        opts_frame = LabelFrame(self, text="Video Feed Options")
        opts_frame.pack()

        Checkbutton(opts_frame, text="Show Ball", variable=self.show_ball_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(opts_frame, text="Show Velocity", variable=self.show_ballv_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(opts_frame, text="Show Robots", variable=self.show_robots_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        # Checkbutton(opts_frame, text="Show Corrections", variable=self.show_correct_var)\
        #     .pack(side=LEFT, padx=10, pady=10, anchor=N)
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

        self.is_recording = False

        video_frame = LabelFrame(self, text="Record Video")

        self.vid_start_btn = Button(video_frame, text="Begin Record", command=self.on_begin_record,
               padx=10, pady=10, width=15)
        self.vid_start_btn.pack(side=LEFT)

        self.vid_end_btn = Button(video_frame, text="End Record", command=self.on_end_record,
               padx=10, pady=10, width=15)
        self.vid_end_btn.pack(side=LEFT)

        self.title_var = UserVariable(self, str, self._get_default_title())
        self.video_entry = Entry(video_frame, textvariable=self.title_var, width=30)
        self.video_entry.pack(padx=10, pady=10)

        video_frame.pack(padx=5, ipadx=5, pady=5, ipady=5)


    def _get_default_title(self):
        from time import localtime, strftime
        return strftime("%Y_%m_%d %H:%M:%S", localtime())


    def on_show_contours_changed(self, var):
        self.vision.gui.draw_contours = bool(var.value)

    def on_show_ball_changed(self, var):
        self.vision.gui.draw_ball = bool(var.value)

    def on_show_ballv_changed(self, var):
        self.vision.gui.draw_ball_velocity = bool(var.value)

    def on_show_robots_changed(self, var):
        self.vision.gui.draw_robots = bool(var.value)

    def on_show_correct_changed(self, var):
        self.vision.gui.draw_correction = bool(var.value)

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

    def on_detach(self):
        self.disintegrate(self.vision)

    def on_deattach(self):
        self.reintegrate(self.vision)

    def on_begin_record(self, *args):
        self.video_entry['state']   = DISABLED
        self.vid_start_btn['state'] = DISABLED
        self.vid_end_btn['state']   = NORMAL

        self.vision.start_video(self.title_var.value)

    def on_end_record(self, *args):
        self.vision.end_video()

        self.title_var.value = self._get_default_title()

        self.vid_end_btn['state']   = DISABLED
        self.video_entry['state']   = NORMAL
        self.vid_start_btn['state'] = NORMAL








