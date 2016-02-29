""" Calibration GUI - (c) SDP Team E 2016
    --------------------------------
    Authors: Jake, James Renwick
    Team: SDP Team E
"""

try:
    import cv2
except:
    cv2 = None

from common import *
from config import Configuration, Calibration

import functools
import numpy as np


class CalibrationUI(UserControl):

    def __init__(self, calibration, parent=None):
        UserControl.__init__(self, parent, "Colour Calibration")

        assert type(calibration) == Calibration
        self.calibration = calibration

        selector_frame = LabelFrame(self, text="Calibration Colours")
        selector_frame.grid(row=0, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.min_frame = LabelFrame(self, text="Minimum Values")
        self.min_frame.grid(row=1, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.max_frame = LabelFrame(self, text="Maximum Values")
        self.max_frame.grid(row=2, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.button_frame = Frame(self)
        self.button_frame.grid(row=3, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        self.text_frame = Frame(self)
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

        Button(self.button_frame, text="Quit", command=self.close,
                padx=10, pady=10, width=15).pack(side=RIGHT)

        Label(self.text_frame, text="Press 'q' to quit").pack()

        # Perform initial update
        self.on_colour_selected()


    @staticmethod
    def create_and_show(calibration):
        CalibrationUI(calibration).show()

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
        if cv2:
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
        #         "Reverting does not write to the file.", icon='warning', parent=self) == 'yes':
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


if __name__ == "__main__":
    CalibrationUI(Configuration.read_calibration(create_if_missing=True), None).show()
