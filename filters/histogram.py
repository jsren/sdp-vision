from filters import Filter

class HistogramFilter(Filter):

    def __init__(self):
        self._settings = dict(red=list(), green=list(), blue=list())

    def __getitem__(self, item):
        return self._settings[item]

    def __setitem__(self, key, value):
        self._settings[key] = value

    def apply(self, gbr_frame):
        colors = ['blue', 'green', 'red']
        t = 0
        for i in range(0, 449):
            for n in range(0, 449):
                t += 1
                p = gbr_frame[i][n]
            #     for c in range(0, 3):
            #         for s in self._settings[colors[c]]:
            #             if p[c] <= s[0]:
            #                 #if s[1] < 0.9 or s[1] > 1.1:
            #                 p[c] = min(255, int(p[c] * s[1]))
            #                 break

