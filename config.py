import os
import json

def _get_machine_name():
    from socket import gethostname
    return gethostname()

class CalibrationSetting(object):

    def __init__(self, json):
        self._data = json

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        if key in ('min', 'max'):
            self._data[key] = list(value)
        else:
            self._data[key] = value

    def get_json(self):
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
    @property
    def min(self): return tuple([float(i) for i in self._data['min']])
    @property
    def max(self): return tuple([float(i) for i in self._data['max']])
    @property
    def blur(self): return int(self._data['blur'])
    @property
    def close(self): return float(self._data['close'])
    @property
    def open(self): return float(self._data['open'])
    @property
    def contrast(self): return float(self._data['contrast'])

    @staticmethod
    def get_default():
        return CalibrationSetting({
            'erode': 0, 'min': [0,0,0], 'max': [255,255,255],
            'blur': 0, 'close': 0, 'open': 0, 'contrast': 0
        })


class Calibration(object):

    def __init__(self, machine_name, json):
        self._machine = machine_name
        self._data    = json

    @property
    def machine_name(self):
        return self._machine

    def get_color_setting(self, pitch, name):
        return CalibrationSetting(self._data[pitch][name])

    def set_color_setting(self, pitch, name, setting):
        self._data[pitch][name] = setting.get_json()

    def get_json(self):
        return self._data

    @staticmethod
    def get_default():
        return Calibration(_get_machine_name(),
            { i : { c : CalibrationSetting.get_default() for c in ['blue', 'yellow', 'red', 'green', 'pink'] }
             for i in [0,1] })


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
    @property
    def contrast(self): return int(self._data['contrast'])
    @property
    def color(self): return int(self._data['color'])
    @property
    def hue(self): return int(self._data['hue'])
    @property
    def red_balance(self): return int(self._data['Red Balance'])
    @property
    def blue_balance(self): return int(self._data['Blue Balance'])

    @staticmethod
    def get_default():
        return VideoConfig(_get_machine_name(), {
            'brightness': 180, 'Blue Balance': 0, 'color': 80,
            'hue': 5, 'Red Balance': 5, 'contrast': 120
        })


class RealTimeVideoConfig(VideoConfig):
    from subprocess import Popen, PIPE

    def __init__(self, machine_name, json):
        super(RealTimeVideoConfig).__init__(machine_name, json)

    def commit(self):
        # Use v4lctl to set only those values which have changed
        for attr in self._changed:
            p = self.Popen(["v4lctl", "setattr", attr, str(self[attr])], stdout=self.PIPE)
            output, _ = p.communicate()

            if output.strip(): print "[V4LCTL] " + output

        self._changed.clear()


class Configuration(object):

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

        # If no machine name specified, use current machine
        if machine_name is None: machine_name = _get_machine_name()

        # Get filepath
        calib_dir  = os.path.dirname(__file__)
        calib_file = os.path.join(calib_dir, "calibrations/" + machine_name + ".json")

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

        # If no machine name specified, use current machine
        if machine_name is None: machine_name = _get_machine_name()

        # Get filepath
        setting_dir  = os.path.dirname(__file__)
        setting_file = os.path.join(setting_dir, "calibrations/" + machine_name + ".json")

        # Save JSON
        with open(setting_file, 'w') as file:
            return json.dump(video_config.get_json(), file)

    @staticmethod
    def commit_video_config(video_config):
        import subprocess
        for attr in Configuration.video_settings:
            p = subprocess.Popen(["v4lctl", "setattr", attr, str(video_config[attr])],
                                 stdout=subprocess.PIPE)
            output, _ = p.communicate()

            if output.strip(): print "[V4LCTL] " + output



Configuration.video_settings = \
    [ "bright", "contrast", "color", "hue", "Red Balance", "Blue Balance" ]
