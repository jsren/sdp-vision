from common import *
from PIL import ImageTk, Image

from os import path

class StatusUI(UserControl):

    def __init__(self, parent=None):
        UserControl.__init__(self, parent, title="Vision Status (WIP)")

        self.img_ball = ImageTk.PhotoImage(Image.open(
            path.join(path.dirname(__file__), "../images/ball.jpg")
        ))
        self.img_noball = ImageTk.PhotoImage(Image.open(
            path.join(path.dirname(__file__), "../images/no_ball.jpg")
        ))

        self.ball_status_var = UserVariable(self.window, False,
                                    self.on_ball_status_changed, 500)

        frame = Frame(self)
        frame.pack(padx=10, pady=10, ipadx=8, ipady=8)

        self.ball_status = Label(frame, image=self.img_noball)
        self.ball_status.pack()

        # Set initial ball status
        self.on_ball_status_changed(self.ball_status_var)


    def on_ball_status_changed(self, var):
        self.ball_status.configure(
            image=self.img_ball if var.value else self.img_noball)

