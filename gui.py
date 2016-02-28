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
from tkColorChooser import askcolor


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


class MinMaxUI:

    def __init__(self, calibration):
        #assert type(calibration) == Calibration

        self.calibration = calibration

        self.form = Tk()
        self.form.wm_title("Set Calibration Values")

        selector_frame = LabelFrame(self.form, text="Calibration Colours")
        selector_frame.grid(row=0, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        min_frame = LabelFrame(self.form, text="Minimum Values")
        min_frame.grid(row=1, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)

        max_frame = LabelFrame(self.form, text="Maximum Values")
        max_frame.grid(row=2, columnspan=1, sticky="WE", padx=5, ipadx=5, pady=5, ipady=5)


        # Holds the currently-selected colour name
        self.colour_var = StringVar()
        self.colour_var.set(Configuration.calibration_colors[0])

        # Create radio buttons for each colour
        for colour in Configuration.calibration_colors:
            rb = Radiobutton(selector_frame, variable=self.colour_var, text=colour,
                             value=colour, command=self.on_colour_selected, padx=5, pady=5)
            rb.pack(side=LEFT)

        # Create scales for values
        self.min_hue = DoubleVar()
        scale1= Scale(min_frame, variable = self.min_hue, command = self.update_min,
                      to = 255, orient = HORIZONTAL, label = "Hue", length = 300)

        self.min_sat = DoubleVar()
        scale2 = Scale(min_frame, variable = self.min_sat, command = self.update_min,
                       to = 255, orient = HORIZONTAL, label = "Saturation", length = 300)

        self.min_val = DoubleVar()
        scale3 = Scale(min_frame, variable = self.min_val, command = self.update_min,
                       to = 255, orient = HORIZONTAL, label = "Value", length = 300)

        self.max_hue = DoubleVar()
        scale4 = Scale(max_frame, variable = self.max_hue, command = self.update_max,
                       to = 255, orient = HORIZONTAL, label = "Hue", length = 300)

        self.max_sat = DoubleVar()
        scale5 = Scale(max_frame, variable = self.max_sat, command = self.update_max,
                       to = 255, orient = HORIZONTAL, label = "Saturation", length = 300)

        self.max_val = DoubleVar()
        scale6 = Scale(max_frame, variable = self.max_val, command = self.update_max,
                       to = 255, orient = HORIZONTAL, label = "Value", length = 300)

        write_config = Button(max_frame, text = "Write Configurations", command = self.config_update)
        write_config.pack(side = BOTTOM)

        values = [scale1, scale2, scale3, scale4, scale5, scale6]

        for val in values:
            val.pack(anchor = W)



    def show(self):
        self.form.mainloop()

    def on_colour_selected(self):
        colour = self.colour_var.get()
        entry = self.calibration[colour]

        self.min_hue.set(entry.min[0])
        self.min_sat.set(entry.min[1])
        self.min_val.set(entry.min[2])
        self.max_hue.set(entry.max[0])
        self.max_sat.set(entry.max[1])
        self.max_val.set(entry.max[2])

    def update_min(self, e):
        colour = self.colour_var.get()
        entry = self.calibration[colour]
        entry['min'] = (self.min_hue.get(), self.min_sat.get(), self.min_val.get())

    def update_max(self, e):
        colour = self.colour_var.get()
        entry = self.calibration[colour]
        entry['max'] = (self.max_hue.get(), self.max_sat.get(), self.max_val.get())

    def config_update(self):
        Configuration.write_calibration(self.calibration, self.calibration.machine_name)








class GUI:

    def __init__(self, pitch):
        self.frame = None
        self.pitch = pitch

        self.config = Configuration.read_video_config(create_if_missing=True)

        # create GUI
        # The first numerical value is the starting point for the vision feed
        cv2.namedWindow('frame2')

        """
        cv2.namedWindow('frame3')

        cv2.createTrackbar('Blue: 0 \n Red: 1 \n Yellow: 2 \n Pink: 3 \n Green: 4','frame3',0,4 ,nothing)
        cv2.createTrackbar('Min H','frame3',0,255,nothing)
        cv2.createTrackbar('Min S','frame3',0,255,nothing)
        cv2.createTrackbar('Min V','frame3',0,255,nothing)
        cv2.createTrackbar('Max H','frame3',0,255,nothing)
        cv2.createTrackbar('Max S','frame3',0,255,nothing)
        cv2.createTrackbar('Max V','frame3',0,255,nothing)
        """



        if pitch == 0:

            cv2.createTrackbar('bright','frame2',180,255,nothing)
            cv2.createTrackbar('contrast','frame2',120,127,nothing)
            cv2.createTrackbar('color','frame2',80,255,nothing)
            cv2.createTrackbar('hue','frame2',5,30,nothing)
            cv2.createTrackbar('Red Balance','frame2',5,20,nothing)
            cv2.createTrackbar('Blue Balance','frame2',0,20,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',1,1,nothing)


        if pitch == 1:
            cv2.createTrackbar('bright','frame2',23000,40000,nothing)
            cv2.createTrackbar('contrast','frame2',28000,40000,nothing)
            cv2.createTrackbar('color','frame2',65000,100000,nothing)
            cv2.createTrackbar('hue','frame2',38000,60000,nothing)
            cv2.createTrackbar('Gaussian blur','frame2',1,1,nothing)



    def drawGUI(self):
        if self.pitch == 0:
            attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
        elif self.pitch == 1:
            attributes = ["bright", "contrast", "color", "hue"]
        else:
            raise RuntimeError("StupidTitException: Incorrect pitch number")

        for att in attributes:
            self.config[att] = cv2.getTrackbarPos(att, 'frame2')
        self.config.commit()


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
