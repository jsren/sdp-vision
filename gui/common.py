from Tkinter import *

class UserControl(Frame):

    def __init__(self, master=None, title=None):
        if master is None:
            master = self.window = Toplevel()
            master.wm_title(title)
            master.resizable(0, 0)
            master.bind("<Key-q>", lambda e: self.close())
        else:
            self.window = None

        Frame.__init__(self, master)


    def show(self):
        self.pack()

    def close(self):
        if self.window:
            self.window.destroy()
        else:
            self.destroy()


class MainWindow(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.geometry("0x0")

    def show(self, windows):
        self.update()
        for w in windows:
            w.show()
        self.mainloop()


    @staticmethod
    def create_and_show(get_windows_func):
        MainWindow().show(get_windows_func())


