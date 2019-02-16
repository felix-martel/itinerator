from xml.etree import ElementTree as ET
import requests

from geo import Point

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
    for ptype in ["village", "town", "suburb", "city"]:
        d = build_query(bbox, place=ptype)
        for locality in d:
            locality["type"] = ptype
            locality["dept"] = locality["zipcode"][:2]
        data = data + d
    return data