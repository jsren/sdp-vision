from Tkinter import *

class UserVariable(object):

    def __init__(self, window, value=None, callback=None, poll_interval=100):
        self.interval = int(poll_interval)
        self.window   = window
        self.callback = callback
        self._value   = value
        self._changed = False
        window.after(poll_interval, self._update)

    def _update(self):
        if self._changed and self.callback:
            self.callback(self)

        self._changed = False
        self.window.after(self.interval, self._update)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._changed = True


class UserControl(Frame):

    def __init__(self, master=None, title=None):
        if master is None:
            master = self.window = Toplevel()
            master.wm_title(title)
            master.resizable(0, 0)
            master.bind("<Key-q>", lambda e: self.close())
        else:
            self.window = master._nametowidget(master.winfo_parent())

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
        self._windows = None

    def show(self, windows):
        self.update()
        self._windows = windows
        for w in windows:
            w.show()
        self.mainloop()

    @property
    def windows(self):
        return self._windows

    @staticmethod
    def create_and_show(get_windows_func):
        MainWindow().show(get_windows_func())


