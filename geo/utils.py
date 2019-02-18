import pyproj
from math import radians, degrees

EARTH_RADIUS = 6373.0
mercator = pyproj.Proj(init="epsg:3857")

def convert(*args, from_unit=None, to_unit=None):
    units = {
        "mm": 0.001,
        "cm": 0.01,
        "dm": 0.1,
        "m": 1,
        "dam": 10,
        "hm": 100,
        "km": 1000
    }
    return tuple([arg * (units[from_unit] / units[to_unit]) for arg in args])

def denivele(elevations):
    dpos = 0
    dneg = 0
    i = 0
    for j in range(1, len(elevations)):
        delta = elevations[j] - elevations[i]
        i = j
        if delta > 0:
            dpos += delta
        else:
            dneg -= delta
    return dpos, dneg