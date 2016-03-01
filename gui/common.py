from Tkinter import *
from threading import current_thread

class UserVariable(Variable, object):

    def __init__(self, window, type, value=None, callback=None, poll_interval=100):
        Variable.__init__(self, window, value=value)

        self.interval = int(poll_interval)
        self.window   = window
        self.callback = callback
        self._value   = value
        self._changed = False
        self._thread  = current_thread().name
        self.type     = type

        window.after(poll_interval, self._update)
        self.trace_variable('w', self._tcl_callback)

    def _update(self):
        if self._changed and self.callback:
            Variable.set(self, self._value)
            self._changed = False
            self.callback(self)

        self.window.after(self.interval, self._update)

    def __del__(self):
        if not hasattr(self, '_thread') or \
                        current_thread().name == self._thread:
            Variable.__del__(self)
        else:
            raise Exception("Cannot delete Tcl variable "
                            "from different thread")

    def _tcl_callback(self, *_):
        self.value = self.type(Variable.get(self))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        assert isinstance(value, self.type)
        self._value   = value
        self._changed = True

    def set(self, value):
        if hasattr(self, '_thread'):
            if not current_thread().name == self._thread:
                raise Exception("Cannot set Tcl variable "
                                "from different thread.")
        Variable.set(self, value)

    def get(self):
        return self.value


class UserControl(Frame):

    def __init__(self, master=None, title=None):
        self._title = title

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

    @property
    def title(self):
        return self._title


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


