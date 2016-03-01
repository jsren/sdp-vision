from common import *
from Tkinter import *
from ttk import *

import numpy as np

class Histogram(Canvas):
    def __init__(self, parent, filter_instance, width, height):
        Canvas.__init__(self, parent, bg='white', width=width, height=height)
        self.filter = filter_instance
        self.width  = width
        self.height = height

        self.shift_state = False
        self.ctrl_state  = False

        self.color = 'red'

        self.bind("<ButtonRelease-1>", self.on_lclick)
        self.bind("<ButtonRelease-3>", self.on_rclick)

        self.redraw()

    def on_lclick(self, evt):
        self.filter[self.color].append((
            (evt.x * 255.0) / self.width,
            ((self.height - evt.y) * 2.0) / self.height,
            np.array((evt.x, evt.y))
        ))
        self.redraw()

    def on_rclick(self, evt):
        min   = None
        mind  = self.width * self.height
        point = np.array((evt.x, evt.y))
        for entry in self.filter[self.color]:
            d = np.linalg.norm(entry[2] - point)
            if d < mind:
                mind = d
                min  = entry

        if min is not None:
            self.filter[self.color].remove(min)
            self.redraw()

    def redraw(self):
        self.delete(ALL)
        p0 = (0, self.height/2)
        pn = (self.width, self.height/2)
        pp = p0
        c = 0
        for color in ['red', 'green', 'blue']:
            self.filter[color].sort(key=lambda e: e[2][0])
            for entry in self.filter[color]:
                fill = [0,0,0]
                fill[c] = entry[0]
                self.create_rectangle(pp[0], 0, entry[2][0], self.height,
                                      fill="#%4.4x%4.4x%4.4x"%(fill[0],fill[1],fill[2]))
                self.create_line(pp[0], pp[1], entry[2][0], entry[2][1], fill=color)
                pp = entry[2]
            self.create_line(pp[0], pp[1], pn[0], pn[1])
            c += 1


class GuiSettingsUI(UserControl):

    def __init__(self, vision_wrapper, master=None):
        UserControl.__init__(self, master, title="GUI Settings")
        self.vision = vision_wrapper

        self.show_contours_var = UserVariable(self, int, True, self.on_show_contours_changed, 500)
        self.show_ball_var = UserVariable(self, int, True, self.on_show_ball_changed, 500)
        self.show_ballv_var = UserVariable(self, int, True, self.on_show_ballv_changed, 500)
        self.show_robots_var = UserVariable(self, int, True, self.on_show_robots_changed, 500)

        overlay_frame = LabelFrame(self, text="Overlay")
        Checkbutton(overlay_frame, text="Show Ball", variable=self.show_ball_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(overlay_frame, text="Show Velocity", variable=self.show_ballv_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(overlay_frame, text="Show Robots", variable=self.show_robots_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        Checkbutton(overlay_frame, text="Show Contours", variable=self.show_contours_var)\
            .pack(side=LEFT, padx=10, pady=10, anchor=N)
        overlay_frame.pack()

        hist_frame = LabelFrame(self, text="Histogram")
        hist = Histogram(hist_frame, vision_wrapper.hist_filter, 500, 200)
        hist.pack()
        hist_frame.pack()


    def on_show_contours_changed(self, var):
        self.vision.gui.draw_contours = bool(var.value)

    def on_show_ball_changed(self, var):
        self.vision.gui.draw_ball = bool(var.value)

    def on_show_ballv_changed(self, var):
        self.vision.gui.draw_ball_velocity = bool(var.value)

    def on_show_robots_changed(self, var):
        self.vision.gui.draw_robots = bool(var.value)
