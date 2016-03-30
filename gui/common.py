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
        self.tkmain = None

        if master is None:
            master = self.window = Toplevel()
            master.wm_title(title)
            master.resizable(0, 0)
            master.bind("<Key-q>", lambda e: self.close())
        else:
            self.window = master._nametowidget(master.winfo_parent())

        Frame.__init__(self, master)

    def show(self, tk=None):
        self.tkmain = tk
        self.pack()

    def close(self):
        if self.tkmain is not None:
            self.tkmain.close_var.value = True
        elif self.window:
            self.window.destroy()
        else:
            self.destroy()

    def disintegrate(self, *args, **kwargs):
        self.destroy()
        self.__class__(*args, **kwargs).show(self.tkmain)

    def reintegrate(self, *args, **kwargs):
        self.tkmain = None
        self.close()

        kwargs['parent'] = MainUI.get_host()
        ctrl = self.__class__(*args, **kwargs)
        MainUI.add_tab(self.title, ctrl)

    @property
    def title(self):
        return self._title


class MainWindow(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.geometry("0x0")
        self._windows = None

        self.close_var = UserVariable(self, bool, False, self.on_close_changed)

    def show(self, windows):
        self.update()
        self._windows = windows
        for w in windows:
            w.show(self)
        self.mainloop()

    def on_close_changed(self, var):
        if var.value:
            self.destroy()


    @property
    def windows(self):
        return self._windows

    @staticmethod
    def create_and_show(get_windows_func):
        MainWindow().show(get_windows_func())


from gui.main import MainUI
