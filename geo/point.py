from math import sin, cos, sqrt, atan2, radians, asin, pi, degrees
import pyproj
import geo.utils
import geopy.distance


class Point:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

    def __getitem__(self, item):
        if item == 0:
            return self.lon
        if item == 1:
            return self.lat
        raise IndexError("Only two coords")

    @classmethod
    def distance(cls, p1, p2):
        p1 = geopy.distance.lonlat(*p1)
        p2 = geopy.distance.lonlat(*p2)
        return geopy.distance.distance(p1, p2).km

    @classmethod
    def from_radians(cls, lat, lon):
        return cls(degrees(lat), degrees(lon))

    def as_radians(self):
        return radians(self.lon), radians(self.lat)

    def as_mercator(self):
        return geo.utils.mercator(self.lon, self.lat)

    @property
    def coords(self):
        return self.lon, self.lat

    @property
    def lonlat(self):
        return self.lon, self.lat

    @property
    def latlon(self):
        return self.lat, self.lon

    def __repr__(self):
        return "Point(lon={p.lon}, lat={p.lat})".format(p=self)

    def __str__(self):
        return str(self.lonlat)

    def offset(self, distance, angle):
        delta = distance / geo.utils.EARTH_RADIUS
        theta = radians(angle)

        lon1, lat1 = self.as_radians()

        lat2 = asin(sin(lat1) * cos(delta) + cos(lat1) * sin(delta) * cos(theta))
        lon2 = lon1 + atan2(sin(theta) * sin(delta) * cos(lat1), cos(delta) - sin(lat1) * sin(lat2))

        return self.from_radians(lon2, lat2)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(lon=self.lon+other.lon, lat=self.lat+other.lat)
        else:
            raise ValueError()

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(lon=self.lon-other.lon, lat=self.lat-other.lat)
        else:
            raise ValueError()

    def __rmul__(self, other):
        return self * other

    def __mul__(self, other):
        return Point(lon=other*self.lon, lat=other*self.lat)

    def __truediv__(self, other):
        return Point(lon=self.lon/other, lat=self.lat/other)


    def move_west(self, distance):
        return self.offset(distance, 270)

    def move_north(self, distance):
        return self.offset(distance, 0)

    def move_east(self, distance):
        return self.offset(distance, 90)

    def move_south(self, distance):
        return self.offset(distance, 180)

    def move_one(self, distance, direction):
        dirs = {"north": 0, "east": 90, "south": 180, "west": 270}
        return self.offset(distance, dirs[direction])

    def move(self, directions):
        dirs = {"north": 0, "east": 90, "south": 180, "west": 270}
        p = self
        for direction, distance in directions.items():
            if direction in dirs:
                direction = dirs[direction]
            p = p.offset(distance, direction)
        return p

# DEMO_1 = Point(lon=2.82383, lat=47.9042)
# DEMO_2 = Point(lon=3.12595, lat=47.82128)
#
# print(DEMO_1)
# print(DEMO_2)
# print(((DEMO_1 + DEMO_2)/2).latlon)
# print(Point.distance(DEMO_1, DEMO_2))
# print("east+5", DEMO_1.move_east(5).latlon)
# print("west+5", DEMO_1.move_west(5).latlon)
# print("north+5", DEMO_1.move_north(5).latlon)
# print("south+5", DEMO_1.move_south(5).latlon)
# print("nw+5", DEMO_1.move_north(5).move_west(10).latlon)