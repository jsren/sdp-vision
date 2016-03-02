# coding=utf-8
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

        self.ball_status = Label(frame, image=self.img_noball)
        self.ball_status.pack(fill=X, padx=15)

        self.ball_loc_label = Label(frame, text = "Ball Location ")
        self.ball_loc_label.pack(fill=X, padx=15)

        self.robot_loc_label = Label(frame, text = "Robot Locations ")
        self.robot_loc_label.pack(fill=X, padx=15)

        self.robot_hed_label = Label(frame, text = "Robot Headings ")
        self.robot_hed_label.pack(fill=X, padx=15)

        self.window.after(300, self.update_vision_values)


    def on_ball_status_changed(self, var):
        self.ball_status.configure(
            image=self.img_ball if var.value else self.img_noball)

    def update_vision_values(self, *_):
        self.ball_loc_label.configure(text = "Ball Location: ({:5.2f}, {:5.2f})"
                                      .format(*self.vision.get_ball_position()))

        robot_str = "\n".join(("[%s\t] ({:5.2f}, {:5.2f})"%n).format(*p)
                  for (n, p) in self.vision.get_all_robots().items())

        heading_str = "\n".join((u"[{0:s}\t] {{:5.2f}}°".format(n)).format(p)
                    for (n, p) in self.vision.get_robot_headings().items())

        self.robot_loc_label.configure(text="Robot Positions:\n" + robot_str)
        self.robot_hed_label.configure(text="Robot Headings:\n" + heading_str)

        self.window.after(300, self.update_vision_values)


