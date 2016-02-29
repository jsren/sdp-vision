""" Vision GUI - (c) SDP Team E 2016
    --------------------------------
    Authors: Andrew, James Renwick
    Team: SDP Team E
"""
# disable maximize
# press q to quit + close button

try:
    import cv2
except:
    pass

from Tkinter import *
from config import Configuration, Calibration
import numpy as np
import tkMessageBox
import threading
import functools


def nothing(x): 
    pass


class HSVSelector:

    def __init__(self, master, onchange=None):
        self.frame    = Frame(master)
        self.onchange = onchange

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def place(self, *args, **kwargs):
        self.frame.place(*args, **kwargs)


class TrackerSettingsUI:

    def __init__(self, trackers):
        self.trackers = trackers

        self.form = Tk()
        self.form.wm_title("Tracker Settings")
        self.form.resizable(0,0)
        self.form.bind("<Key-q>", lambda e: self.form.destroy())

        row = 0
        for tracker in trackers:
            frame = LabelFrame(self.form, text=tracker.__name__.title() + " Settings")
            frame.grid(row=row, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)
            row += 1
            try:
                tracker.draw_ui(frame)
            except Exception, e:
                print e

    def show(self):
        self.form.mainloop()


class MinMaxUI:

    def __init__(self, calibration):
        assert type(calibration) == Calibration

        self.calibration = calibration

        self.form = Tk()
        self.form.wm_title("Set Calibration Values")
        self.form.resizable(0,0)
        self.form.bind("<Key-q>", lambda e: self.form.destroy())

        selector_frame = LabelFrame(self.form, text="Calibration Colours")
        selector_frame.grid(row=0, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.min_frame = LabelFrame(self.form, text="Minimum Values")
        self.min_frame.grid(row=1, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.max_frame = LabelFrame(self.form, text="Maximum Values")
        self.max_frame.grid(row=2, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.button_frame = Frame(self.form)
        self.button_frame.grid(row=3, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.text_frame = Frame(self.form)
        self.text_frame.grid(row=4, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        # Holds the currently-selected colour name
        self.colour_var = StringVar()
        self.colour_var.set(Configuration.calibration_colors[0])

        # Create radio buttons for each colour
        for colour in Configuration.calibration_colors:
            rb = Radiobutton(selector_frame, variable=self.colour_var, text=colour.title(),
                             value=colour, command=self.on_colour_selected, padx=5, pady=5)
            rb.pack(side=LEFT)

        # Get specific functions
        min_changed = functools.partial(self.on_slider_changed, 'min')
        max_changed = functools.partial(self.on_slider_changed, 'max')

        self.min_subframe = Frame(self.min_frame)
        self.min_subframe.pack(side=LEFT)

        self.max_subframe = Frame(self.max_frame)
        self.max_subframe.pack(side=LEFT)

        # Create scales for values
        self.min_hue = DoubleVar()
        Scale(self.min_subframe, variable=self.min_hue, command=min_changed,
                      to=179, orient=HORIZONTAL, label="Hue", length=300).pack(anchor=W)
        self.min_sat = DoubleVar()
        Scale(self.min_subframe, variable=self.min_sat, command=min_changed,
                       to=255, orient=HORIZONTAL, label="Saturation", length=300).pack(anchor=W)
        self.min_val = DoubleVar()
        Scale(self.min_subframe, variable=self.min_val, command=min_changed,
                       to=255, orient=HORIZONTAL, label="Value", length=300).pack(anchor=W)
        self.max_hue = DoubleVar()
        Scale(self.max_subframe, variable=self.max_hue, command=max_changed,
                       to=179, orient=HORIZONTAL, label="Hue", length=300).pack(anchor=W)
        self.max_sat = DoubleVar()
        Scale(self.max_subframe, variable=self.max_sat, command=max_changed,
                       to=255, orient=HORIZONTAL, label="Saturation", length=300).pack(anchor=W)
        self.max_val = DoubleVar()
        Scale(self.max_subframe, variable=self.max_val, command=max_changed,
                       to=255, orient=HORIZONTAL, label="Value", length=300).pack(anchor=W)

        self.canvas_min = Canvas(self.min_frame, width=200, height=200, bg='black')
        self.canvas_min.pack(side=RIGHT, padx=15)

        self.canvas_max = Canvas(self.max_frame, width=200, height=200, bg='black')
        self.canvas_max.pack(side=RIGHT, padx=15)

        # Buttons
        Button(self.button_frame, text="Write Configurations", command=self.config_update,
               padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Reload from File", command=self.reload_config,
                padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Revert to Default", command=self.revert_default,
                padx=10, pady=10, width=15).pack(side=LEFT)

        Button(self.button_frame, text="Quit", command=self.form.destroy,
                padx=10, pady=10, width=15).pack(side=RIGHT)

        Label(self.text_frame, text="Press 'q' to quit").pack()

        # Perform initial update
        self.on_colour_selected()

    def show(self):
        self.form.mainloop()

    @staticmethod
    def create_and_show(calibration):
        MinMaxUI(calibration).show()

    def on_colour_selected(self):
        colour = self.colour_var.get()
        entry = self.calibration[colour]

        self.min_hue.set(entry.min[0])
        self.min_sat.set(entry.min[1])
        self.min_val.set(entry.min[2])
        self.max_hue.set(entry.max[0])
        self.max_sat.set(entry.max[1])
        self.max_val.set(entry.max[2])
        self.update_swatches('min')
        self.update_swatches('max')


    def on_slider_changed(self, minmax, _):
        entry = self.calibration[self.colour_var.get()]
        if minmax == 'min':
            entry.min = (self.min_hue.get(), self.min_sat.get(), self.min_val.get())
        elif minmax == 'max':
            entry.max = (self.max_hue.get(), self.max_sat.get(), self.max_val.get())
        else:
            raise Exception("Invalid value for parameter 'minmax'")
        # Update swatch
        self.update_swatches(minmax)


    def update_swatches(self, minmax):
        if minmax == 'min':
            canvas = self.canvas_min
            hsv = np.uint8([[[self.min_hue.get(), self.min_sat.get(), self.min_val.get()]]])
        elif minmax == 'max':
            canvas = self.canvas_max
            hsv = np.uint8([[[self.max_hue.get(), self.max_sat.get(), self.max_val.get()]]])
        else:
            raise Exception("Invalid value for parameter 'minmax'")

        # Convert colour to RGB & set canvas bg
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        canvas.configure(bg='#%02x%02x%02x' % (rgb[0][0][0], rgb[0][0][1], rgb[0][0][2]))


    def config_update(self):
        # if tkMessageBox.askquestion("Write to File", "Are you sure you wish to "
        #     "commit your settings to file '%s'?\nThis will overwrite your current ones.\n"
        #     "This cannot be undone!" %(self.calibration.machine_name+".json"), icon='warning') == 'yes':
        Configuration.write_calibration(self.calibration, self.calibration.machine_name)

    def revert_default(self):
        # if tkMessageBox.askquestion("Revert to Default", "Are you sure you wish to "
        #         "revert to default settings?\nThis will overwrite your current ones.\n"
        #         "Reverting does not write to the file.", icon='warning', parent=self.form) == 'yes':
        default = Calibration.get_default()
        for colour in default:
            self.calibration[colour] = default[colour]

        # Now update UI to reflect change
        self.on_colour_selected()

    def reload_config(self):
        # if tkMessageBox.askquestion("Reload from File", "Are you sure you wish to "
        #         "reload settings from file?\nThis will overwrite your current ones.\n"
        #         "This cannot be undone!", icon='warning') == 'yes':
        config = Configuration.read_calibration(self.calibration.machine_name)
        for colour in config:
            self.calibration[colour] = config[colour]

        # Now update UI to reflect change
        self.on_colour_selected()


class GUI:

    def __init__(self, pitch, color_settings, calibration):
        self.frame = None
        self.pitch = pitch
        self.color_settings = color_settings

        self.calibration = calibration
        self.config      = Configuration.read_video_config(create_if_missing=True)

        # create GUI
        # The first numerical value is the starting point for the vision feed
        cv2.namedWindow('frame2')

        if self.color_settings in [0, "small"]:
            cv2.createTrackbar('bright','frame2',self.config.brightness,255,nothing)
            cv2.createTrackbar('contrast','frame2',self.config.contrast,127,nothing)
            cv2.createTrackbar('color','frame2',self.config.color,255,nothing)
            cv2.createTrackbar('hue','frame2',self.config.hue,30,nothing)
            cv2.createTrackbar('Red Balance','frame2',self.config.red_balance,20,nothing)
            cv2.createTrackbar('Blue Balance','frame2',self.config.blue_balance,20,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',0,1,nothing)

        if self.color_settings in [1, "big"]:
            cv2.createTrackbar('bright','frame2',self.config.brightness,40000,nothing)
            cv2.createTrackbar('contrast','frame2',self.config.contrast,40000,nothing)
            cv2.createTrackbar('color','frame2',self.config.color,100000,nothing)
            cv2.createTrackbar('hue','frame2',self.config.hue,60000,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',0,1,nothing)



    def drawGUI(self):
        if self.color_settings in [0, "small"]:
            attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
        elif self.color_settings in [1, "big"]:
            attributes = ["bright", "contrast", "color", "hue"]
        else:
            raise RuntimeError("StupidTitException: Incorrect color_settings value. Choose from the set [0, small, 1, big]")

        for att in attributes:
            self.config[att] = cv2.getTrackbarPos(att, 'frame2')
        self.config.commit()

    def commit_settings(self):
        for attr in self.config:
            self.config[attr] = cv2.getTrackbarPos(attr, 'frame2')
        Configuration.write_video_config(self.config, self.config.machine_name)


    def warp_image(self, frame):
        # TODO: this might work in gui, but are the blur values saved anywhere?
        # TODO: implement blur value variations
        """
        Creates trackbars and applies frame preprocessing for functions that actually require a frame,
        instead of setting the video device options
        :param frame: frame
        :return: preprocessed frame
        """
        blur = cv2.getTrackbarPos('Gaussian blur', 'frame2')

        if blur >= 1:
            if blur % 2 == 0:
                blur += 1
            frame = cv2.GaussianBlur(frame, (121, 121), 0)

        return frame


if __name__ == "__main__":
    MinMaxUI(Configuration.read_calibration()).show()
