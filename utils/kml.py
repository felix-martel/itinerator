from fastkml import kml
from geo import Point
from shapely.geometry import Polygon

VERSION = '{http://www.opengis.net/kml/2.2}'


def extract_track(k):
    doc = list(k.features())[0]
    track = list(doc.features())[0]
    return track


def read_kml(fname):
    with open(fname, "rt", encoding="utf-8") as f:
        doc = f.read().encode("utf-8")
    k = kml.KML()
    k.from_string(doc)
    return k


def read_track(fname, max_points=None):
    k = read_kml(fname)
    track = extract_track(k)
    name = track.name
    points = []
    for line in track.geometry.geoms:
        for lon, lat, alt in line.coords:
            points.append(Point(lon, lat))
            if max_points is not None and len(points) == max_points:
                return points, name
    return points, name

def placemark(pid, name="", description=""):
    return kml.Placemark(VERSION, str(pid), name, description)

def rectangle(lon_min, lon_max, lat_min, lat_max):
    west, east, south, north = lon_min, lon_max, lat_min, lat_max
    path = [
        (west, north, 0),
        (east, north, 0),
        (east, south, 0),
        (west, south, 0)
    ]
    return Polygon(path)

def document(name='', description='', shapes=[]):
    k = kml.KML()

    d = kml.Document(VERSION, 'root', 'Boxes', '')
    k.append(d)

    f = kml.Folder(VERSION, 'content', name, description)
    d.append(f)

    for shape in shapes:
        f.append(shape)
    return k