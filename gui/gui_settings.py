from common import *
from Tkinter import *
from ttk import *

class GuiSettingsUI(UserControl):

    def __init__(self, vision_wrapper, master=None):
        UserControl.__init__(self, master, title="GUI Settings")
        self.vision = vision_wrapper

        self.show_contours_var = UserVariable(self, int, True, self.on_show_contours_changed, 500)
        self.show_ball_var = UserVariable(self, int, True, self.on_show_ball_changed, 500)
        self.show_ballv_var = UserVariable(self, int, True, self.on_show_ballv_changed, 500)
        self.show_robots_var = UserVariable(self, int, True, self.on_show_robots_changed, 500)
        self.show_raw_var = UserVariable(self, int, True, self.on_show_raw_changed, 500)

        Checkbutton(self, text="Show Ball", variable=self.show_ball_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(self, text="Show Velocity", variable=self.show_ballv_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(self, text="Show Robots", variable=self.show_robots_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(self, text="Show Contours", variable=self.show_contours_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(self, text="Enable Raw Video", variable=self.show_raw_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)

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
