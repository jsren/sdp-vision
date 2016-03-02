""" config.py - (c) SDP Team E 2016
    --------------------------------
    Authors: James Renwick
    Team: SDP Team E
"""

import os
import json

def _get_machine_name():
    from socket import gethostname
    return gethostname()

class CalibrationSetting(object):
    """ Object representing a colour entry inside a calibration file. """

    def __init__(self, json):
        """
        :param json: The dictionary representation of the colour entry.
        """
        self._data = json

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def get_json(self):
        """ Gets the underlying JSON object.
        :return: The dictionary representation of the colour entry.
        """
        self._data['erode']    = float(self._data['erode'])
        self._data['blur']     = int(self._data['blur'])
        self._data['close']    = float(self._data['close'])
        self._data['open']     = float(self._data['open'])
        self._data['contrast'] = int(self._data['contrast'])
        self._data['min']      = tuple([float(i) for i in self._data['min']])
        self._data['max']      = tuple([float(i) for i in self._data['max']])
        return self._data

    @property
    def erode(self): return float(self._data['erode'])
    @erode.setter
    def erode(self, value): self._data['erode'] = float(value)
    @property
    def min(self): return tuple([float(i) for i in self._data['min']])
    @min.setter
    def min(self, value): self._data['min'] = tuple([float(i) for i in value])
    @property
    def max(self): return tuple([float(i) for i in self._data['max']])
    @max.setter
    def max(self, value): self._data['max'] = tuple([float(i) for i in value])
    @property
    def blur(self): return int(self._data['blur'])
    @blur.setter
    def blur(self, value): self._data['blur'] = int(value)
    @property
    def close(self): return float(self._data['close'])
    @close.setter
    def close(self, value): self._data['close'] = float(value)
    @property
    def open(self): return float(self._data['open'])
    @open.setter
    def open(self, value): self._data['open'] = float(value)
    @property
    def contrast(self): return float(self._data['contrast'])
    @contrast.setter
    def contrast(self, value): self._data['contrast'] = float(value)

    @staticmethod
    def get_default():
        """ Gets a new `CalibrationSetting` instance initialised
        with default values.
        :return: A new `CalibrationSetting` instance.
        """
        return CalibrationSetting({
            'erode': 0, 'min': [0,0,0], 'max': [255,255,255],
            'blur': 0, 'close': 0, 'open': 0, 'contrast': 0
        })


class Calibration(object):

    def __init__(self, machine_name, json):
        self._machine = machine_name
        self._data    = json

    def __getitem__(self, item):
        return CalibrationSetting(self._data[item])

    def __setitem__(self, key, value):
        assert type(value) == CalibrationSetting
        self._data[key] = value.get_json()

    def __iter__(self):
        return iter(Configuration.calibration_colors)

    @property
    def machine_name(self):
        return self._machine

    def get_json(self):
        return self._data

    @staticmethod
    def get_default():
        try:
            return Configuration.read_calibration("default", create_if_missing=False)
        except:
            return Calibration(_get_machine_name(),
                { c : CalibrationSetting.get_default().get_json()
                             for c in Configuration.calibration_colors })


class VideoConfig(object):

    _changed = set()

    def __init__(self, machine_name, json):
        self._data    = json
        self._machine = machine_name

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        if self._data[key] != value:
            self._changed.add(key)
        self._data[key] = value

    def __iter__(self):
        return iter(Configuration.video_settings)

    def get_json(self):
        self._data['bright']       = int(self._data['bright'])
        self._data['contrast']     = int(self._data['contrast'])
        self._data['color']        = int(self._data['color'])
        self._data['hue']          = int(self._data['hue'])
        self._data['Red Balance']  = int(self._data['Red Balance'])
        self._data['Blue Balance'] = int(self._data['Blue Balance'])
        return self._data

    @property
    def machine_name(self): return self._machine

    @property
    def brightness(self): return int(self._data['bright'])
    @brightness.setter
    def brightness(self, value): self._data['bright'] = int(value)
    @property
    def contrast(self): return int(self._data['contrast'])
    @contrast.setter
    def contrast(self, value): self._data['contrast'] = int(value)
    @property
    def color(self): return int(self._data['color'])
    @color.setter
    def color(self, value): self._data['color'] = int(value)
    @property
    def hue(self): return int(self._data['hue'])
    @hue.setter
    def hue(self, value): self._data['hue'] = int(value)
    @property
    def red_balance(self): return int(self._data['Red Balance'])
    @red_balance.setter
    def red_balance(self, value): self._data['Red Balance'] = int(value)
    @property
    def blue_balance(self): return int(self._data['Blue Balance'])
    @blue_balance.setter
    def blue_balance(self, value): self._data['Blue Balance'] = int(value)

    @staticmethod
    def get_default():
        return VideoConfig(_get_machine_name(), {
            'bright': 180, 'Blue Balance': 0, 'color': 80,
            'hue': 5, 'Red Balance': 5, 'contrast': 120
        })


class RealTimeVideoConfig(VideoConfig):
    from subprocess import Popen, PIPE

    def __init__(self, machine_name, json):
        super(RealTimeVideoConfig, self).__init__(machine_name, json)

    def commit(self):
        # Use v4lctl to set only those values which have changed
        for attr in self._changed:
            p = self.Popen(["v4lctl", "setattr", attr, str(self[attr])], stdout=self.PIPE)
            output, _ = p.communicate()

            if output.strip(): print "[V4LCTL] " + output

        self._changed.clear()


class Configuration(object):

    video_settings = \
    [ "bright", "contrast", "color", "hue", "Red Balance", "Blue Balance" ]

    calibration_colors = \
    [ 'blue', 'yellow', 'red', 'green', 'pink' ]

    video_settings_max = {
        'big': {"bright": 40000, "contrast": 40000, "color":100000, "hue": 60000},
        'small': { "bright": 255, "contrast": 127, "color": 40, "hue": 255, "Red Balance":15, "Blue Balance": 15}
    }


    @staticmethod
    def read_calibration(machine_name=None, create_if_missing=False):

        # If no machine name specified, use current machine
        if machine_name is None: machine_name = _get_machine_name()

        # Open existing file
        calib_dir  = os.path.dirname(__file__)
        calib_file = os.path.join(calib_dir, "calibrations/" + machine_name + ".json")

        # If asked to create if missing, initialise a default calibration
        # for this machine name
        if create_if_missing and not os.path.exists(calib_file):
            Configuration.write_calibration(Calibration.get_default())

        # Parse JSON
        with open(calib_file, 'r') as file:
            return Calibration(machine_name, json.load(file))


    @staticmethod
    def write_calibration(calibration, machine_name=None):
        assert type(calibration) == Calibration

        # If no machine name specified, use current machine
        if machine_name is None: machine_name = _get_machine_name()

        # Get filepath
        calib_dir  = os.path.join(os.path.dirname(__file__), "calibrations/")
        calib_file = os.path.join(calib_dir, machine_name + ".json")

        # Make directory calibrations/ if not already there
        if not os.path.exists(calib_dir):
            os.mkdir(calib_dir)

        # Save JSON
        with open(calib_file, 'w') as file:
            return json.dump(calibration.get_json(), file)


    @staticmethod
    def read_video_config(machine_name=None, create_if_missing=False):

        # If no machine name specified, use current machine
        if machine_name is None: machine_name = _get_machine_name()

        # Get filepath
        setting_dir  = os.path.dirname(__file__)
        setting_file = os.path.join(setting_dir, "settings/" + machine_name + ".json")

        # If asked to create if missing, initialise a default calibration
        # for this machine name
        if create_if_missing and not os.path.exists(setting_file):
            Configuration.write_video_config(VideoConfig.get_default())

        # Parse JSON
        with open(setting_file, 'r') as file:
            return RealTimeVideoConfig(machine_name, json.load(file))


    @staticmethod
    def write_video_config(video_config, machine_name=None):
        assert isinstance(video_config, VideoConfig)

        # If no machine name specified, use current machine
        if machine_name is None: machine_name = _get_machine_name()

        # Get filepath
        setting_dir  = os.path.join(os.path.dirname(__file__), "settings/")
        setting_file = os.path.join(setting_dir, machine_name + ".json")

        # Make directory settings/ if not already there
        if not os.path.exists(setting_dir):
            os.mkdir(setting_dir)

        # Save JSON
        with open(setting_file, 'w') as file:
            return json.dump(video_config.get_json(), file)

    @staticmethod
    def commit_video_config(video_config):
        assert type(video_config) == VideoConfig

        import subprocess
        for attr in Configuration.video_settings:
            p = subprocess.Popen(["v4lctl", "setattr", attr, str(video_config[attr])],
                                 stdout=subprocess.PIPE)
            output, _ = p.communicate()

            if output.strip(): print "[V4LCTL] " + output

