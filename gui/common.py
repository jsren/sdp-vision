from Tkinter import *

class UserControl(Frame):

    def __init__(self, master=None, title=None):
        if master is None:
            master = self.window = Tk()
            master.wm_title(title)
            master.resizable(0, 0)
            master.bind("<Key-q>", lambda e: self.close())
        else:
            self.window = None

        Frame.__init__(self, master)


    def show(self):
        if self.window:
            self.pack()
            self.window.mainloop()
        else:
            self.pack()

    def close(self):
        if self.window:
            self.window.destroy()
        else:
            self.destroy()

