from math import floor

in_to_cm = 2.54

def to_cm(*args):
    return tuple([arg * in_to_cm for arg in args])

def to_inch(*args):
    return tuple([arg / in_to_cm for arg in args])

class Format:
    def __init__(self, cm=None, inch=None, name=None, dpi=None):
        if inch is not None:
            self.w, self.h = inch
            format = "{}x{}in".format(self.w, self.h)
        else:
            self.w, self.h = to_inch(*cm)
            format = "{}x{}cm".format(*cm)
        self.name = format if name is None else name
        self.dpi = dpi

    def __call__(self, *args, **kwargs):
        dpi = args[0]
        return Format(inch=(self.w, self.h), name=self.name, dpi=dpi)

    @property
    def aspect_ratio(self):
        return self.h / self.w

    @property
    def cm(self):
        return to_cm(self.w, self.h)

    @property
    def inch(self):
        return self.w, self.h

    @property
    def px(self):
        return floor(self.dpi * self.w), floor(self.dpi * self.h)

    def to_px(self, dpi):
        return floor(dpi * self.w), floor(dpi * self.h)

A4 = Format(cm=(21, 29.7), name="A4")
A3 = Format(cm=(29.7, 42), name="A3")
A2 = Format(cm=(42, 59.4), name="A2")
A1 = Format(cm=(59.4, 84.1), name="A1")
A0 = Format(cm=(84.1, 118.9), name="A0")
letter = Format(inch=(8.5, 11), name="letter")
legal = Format(inch=(8.5, 14), name="legal")