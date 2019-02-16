from geo.point import Point

NW = Point(lon=2.82383, lat=47.9042)
SE = Point(lon=3.12595, lat=47.82128)
SW = Point(lat=47.82183, lon=2.82414)
NE = Point(lat=47.90613, lon=3.12489)

P1 = NW
P2 = Point(lat=47.8227, lon=2.89761)
P3 = Point(lat=47.86971, lon=3.12489)

path = [P1, P2, P3]


class Bbox:
    def __init__(self, lon_min=None, lon_max=None, lat_min=None, lat_max=None):
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max
        self._update()

    @property
    def box(self):
        return (self.lon_min, self.lon_max, self.lat_min, self.lat_max)

    @property
    def is_empty(self):
        return self.lon_min is None or self.lon_max is None or self.lat_min is None or self.lat_max is None

    def _update(self):
        if self.is_empty:
            self.b_lon, self.b_lat = 0, 0
        else:
            self.b_lon, self.b_lat = self.compute_dims()

    def compute_dims(self):
        width = Point.distance(self.west, self.east)
        height = Point.distance(self.north, self.south)
        return width, height

    @property
    def b(self):
        return self.b_lon, self.b_lat

    @property
    def dim(self):
        return self.b_lon, self.b_lat

    @classmethod
    def from_points(cls, points):
        b = cls()
        b.add(points)
        return b

    def _add(self, p):
        if self.is_empty:
            self.lon_min = p.lon
            self.lon_max = p.lon
            self.lat_min = p.lat
            self.lat_max = p.lat
            self._update()
        else:
            if p.lon > self.lon_max:
                self.lon_max = p.lon
            if p.lon < self.lon_min:
                self.lon_min = p.lon
            if p.lat > self.lat_max:
                self.lat_max = p.lat
            if p.lat < self.lat_min:
                self.lat_min = p.lat
            self._update()

    def add(self, p):
        if isinstance(p, Point):
            self._add(p)
        else:
            for point in p:
                self._add(point)

    def __and__(self, other):
        if isinstance(other, Point):
            b = Bbox(*self.box)
            b.add(other)
            return b

    def __lt__(self, other):
        """self < other"""
        b_max, b_min = max(*other), min(*other)
        return (max(*self.b) < b_max) and (min(*self.b) < b_min)

    def __le__(self, other):
        """self < other"""
        b_max, b_min = max(*other), min(*other)
        return (max(*self.b) <= b_max) and (min(*self.b) <= b_min)

    def __gt__(self, other):
        """self < other"""
        b_max, b_min = max(*other), min(*other)
        return (max(*self.b) > b_max) and (min(*self.b) > b_min)

    def __ge__(self, other):
        """self < other"""
        b_max, b_min = max(*other), min(*other)
        return (max(*self.b) >= b_max) and (min(*self.b) >= b_min)

    @property
    def coordinates(self):
        return self.box

    @property
    def south(self):
        return 0.5 * (self.southeast + self.southwest)

    @property
    def north(self):
        return 0.5 * (self.northeast + self.northwest)

    @property
    def west(self):
        return 0.5 * (self.northwest + self.southwest)

    @property
    def east(self):
        return 0.5 * (self.northeast + self.southeast)

    @property
    def northwest(self):
        return Point(self.lon_min, self.lat_max)

    @property
    def southwest(self):
        return Point(self.lon_min, self.lat_min)

    @property
    def northeast(self):
        return Point(self.lon_max, self.lat_max)

    @property
    def southeast(self):
        return Point(self.lon_max, self.lat_min)

    def __getitem__(self, item):
        return self.box[item]

    def expand(self, lon=0, lat=0):
        lon_min, lat_min = self.southwest.move_south(lat).move_west(lon)
        lon_max, lat_max = self.northeast.move_north(lat).move_east(lon)
        return Bbox(lon_min, lon_max, lat_min, lat_max)

    def expand_to(self, target_dim):
        w, h = self.dim
        if w > h:
            w_target, h_target = max(target_dim), min(target_dim)
        else:
            w_target, h_target = min(target_dim), max(target_dim)
        dw = (w_target - w) / 2
        dh = (h_target - h) / 2

        b = self
        if dw > 0:
            b = b.expand(lon=dw)
        if dh > 0:
            b = b.expand(lat=dh)
        return b

    def __contains__(self, item):
        assert isinstance(item, Point)
        lon, lat = item
        return (self.lon_min <= lon) and (self.lon_max >= lon) and (self.lat_min <= lat) and (self.lat_max >= lat)
