from collections import namedtuple
from xml.etree import ElementTree as ET
import requests

import geo
from geo import Point

City = namedtuple("City", ["name", "dept"])

OVERPASS_ENDPOINT = "http://www.overpass-api.de/api/xapi?node[bbox={w:.4f},{s:.4f},{e:.4f},{n:.4f}][place={place}]"


def parse_file(fname):
    root = ET.parse(fname).getroot()
    return parse_xml(root)

def parse_string(s):
    root = ET.fromstring(s)
    return parse_xml(root)

def parse_xml(xml):
    cities = []
    for node in xml:
        if node.tag == "node":
            lon = float(node.attrib["lon"])
            lat = float(node.attrib["lat"])
            id_ = node.attrib["id"]
            city = {
                "name": id_,
                "pos": Point(lon, lat),
                "population": 0,
                "zipcode": "UNKNOWN"
            }
            ctable = {
                "name": "name",
                "population": "population",
                "ref:INSEE": "zipcode"
            }
            for data in node:
                if data.tag == "tag":
                    key, value = data.attrib["k"], data.attrib["v"]
                    if key in ctable:
                        new_key = ctable[key]
                        city[new_key] = value
            city["population"] = int(city["population"])
            cities.append(city)
        else:
            # Not a 'node' tag
            pass
    return cities

def build_query(bbox, place="village"):
    w, e, s, n = bbox
    url = OVERPASS_ENDPOINT.format(w=w, e=e, s=s, n=n, place=place)
    r = requests.get(url)
    if r.status_code == 200:
        return parse_string(r.content)
    else:
        print("ERROR")
        return []

def get_places(bbox):
    data = []
    types = ["village", "town", "city"] # ["village", "town", "suburb", "city"]
    for ptype in types:
        d = build_query(bbox, place=ptype)
        for locality in d:
            locality["type"] = ptype
            locality["dept"] = locality["zipcode"][:2]
        data = data + d
    return data

def rank(city, func):
    score = func(city)
    return score, city["dept"], city["name"]

def _significance(city):
    pop = 0
    t = -1
    if "population" in city:
        pop = city["population"]
    if "type" in city:
        t = ["hamlet", "village", "suburb", "town", "city"].index(city["type"])
    return t, pop

def rank_by_significance(city):
    return rank(city, func=_significance)

def rank_by_distance(city, ref):
    dist = lambda city: geo.Point.distance(ref, city["pos"])
    return rank(city, func=dist)