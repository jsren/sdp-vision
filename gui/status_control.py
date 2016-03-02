from common import *
from PIL import ImageTk, Image

from os import path

class StatusUI(UserControl):

    def __init__(self, vision, parent=None):
        UserControl.__init__(self, parent, title="Vision Status (WIP)")

        self.vision = vision

        self.img_ball = ImageTk.PhotoImage(Image.open(
            path.join(path.dirname(__file__), "../images/ball.jpg")
        ))
        self.img_noball = ImageTk.PhotoImage(Image.open(
            path.join(path.dirname(__file__), "../images/no_ball.jpg")
        ))

        self.ball_status_var = UserVariable(self.window, bool, False,
                                    self.on_ball_status_changed, 500)

        frame = Frame(self)
        frame.pack(padx=10, pady=10, ipadx=8, ipady=8)

        self.ball_status = Label(frame, image=self.img_noball).pack(anchor=W)


        self.ball_loc_label = Label(frame, text = "Ball Location " + str(self.vision.get_ball_pos())).pack(anchor=W)

        self.robot_loc_label = Label(frame, text = "Robot Locations " + str(self.vision.get_all_robots())).pack(anchor=W)

        self.robot_hed_label = Label(frame, text = "Robot Headings " + str(self.vision.get_robot_headings())).pack(anchor=W)

                                  # Set initial ball status
        self.on_ball_status_changed(self.ball_status_var)

        self.window.after(300, self.update_vision_values)


    def on_ball_status_changed(self, var):
        self.ball_status.configure(
            image=self.img_ball if var.value else self.img_noball)

    def update_vision_values(self, *_):
        self.ball_loc_label.configure(text = "Ball Location" + str(self.vision.get_ball_pos()))
        self.robot_loc_label.configure(text = "Robot Locations " + str(self.vision.get_all_robots()))
        self.robot_hed_label.configure(text = "Robot Headings " + str(self.vision.get_robot_headings()))

        self.window.after(300, self.update_vision_values)


