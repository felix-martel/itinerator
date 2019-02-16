import kml
import geo
import ign
import format
import overpass

class TrackSegment:
    current = 0

    def __init__(self, bbox, start, end, sid=None, raw_bbox=None, name=None, coords=None, descr=None, data={}):
        self.box = bbox
        self.start = start
        self.end = end
        self.raw_bbox = bbox if raw_bbox is None else raw_bbox
        if sid is None:
            sid = TrackSegment.current
            TrackSegment.current += 1
        self.id = sid
        self.coords = coords
        self.data = data
        name, descr = self.generate_name(name, descr)
        self.name = name
        self.descr = descr

    def to_kml(self):
        p = kml.placemark(
            "box-{id}".format(id=self.id),
            self.name,
            "Track segment from points {start} to {curr}".format(start=self.start, curr=self.end)
        )
        p.geometry = kml.rectangle(*self.box)
        return p

    @classmethod
    def _encode_name(cls, name):
        return str(name).replace(" ", "_").replace("'", "-").replace("/", "-")

    def generate_name(self, name, descr):
        if name is not None:
            return name, descr
        else:
            return "segment_{:02d}".format(self.id), "Points {} to {}".format(self.start, self.end)


    def get_coords(self, *args, **kwargs):
        pass

    @property
    def n_cols(self):
        if self.coords is None:
            return None
        c0, _, c1, _ = self.coords
        return c1 - c0

    @property
    def n_rows(self):
        if self.coords is None:
            return None
        _, r0, _, r1 = self.coords
        return r1 - r0

    @property
    def dim(self):
        if self.coords is None:
            return None
        return self.n_rows, self.n_cols

    #def refine_coords(self, target_dim):

    #def get(self, layer=ign.layer.DEFAULT, level=ign.DEFAULT_ZOOM, mset=ign.MSET):

    #def save(self, fname, **kwargs):


class TrackSegmentSet:
    def __init__(self, segments, path, format, zoom, margin):
        self.segments = segments
        self.zoom = zoom
        self.path = path
        self.format = format
        self.margin = margin
        self.name = ""
        self.descr = ""

    @classmethod
    def from_path(cls, path, format=format.A4, zoom=ign.zoom.DEFAULT, margin=0.5):
        curr = 0
        segments = []
        while curr < len(path):
            bbox, raw_bbox, start, curr = cls.segmentize(path, curr, format, zoom, margin)
            segment_id = len(segments)
            # Overpass API here
            cities = overpass.get_places(bbox.expand(1, 1))
            name, descr = cls.process_city_list(cities, path, start, curr, segment_id)
            # Find coords here
            segments.append(TrackSegment(bbox, start=start, end=curr, sid=segment_id, raw_bbox=raw_bbox, data=cities, name=name, descr=descr))

        return cls(segments, path, format, zoom, margin)

    @classmethod
    def process_city_list(cls, cities, path, start, end, sid):
        def rank(city):
            pop = 0
            t = -1
            if "population" in city:
                pop = city["population"]
            if "type" in city:
                t = ["hamlet", "village", "suburb", "town", "city"].index(city["type"])
            return (t, pop, city["name"])
        _, _, main_city = max([rank(city) for city in cities])
        starting_point = path[start]
        ending_point = path[end]

        _, from_city, from_dept = min([(geo.Point.distance(starting_point, city["pos"]), city["dept"], city["name"]) for city in cities])
        _, to_city, to_dept = min([(geo.Point.distance(ending_point, city["pos"]), city["dept"], city["name"]) for city in cities])

        short_name = "Etape {:02d} : {}".format(sid, main_city)
        long_name = "Etape {:02d} : de {} ({}) à {} ({})".format(sid, from_city, from_dept, to_city, to_dept)
        return short_name, long_name

    @classmethod
    def segmentize(cls, path, start, format, zoom, margin):
        w, h = format.cm
        w, h, m = ign.levels[zoom].rescale(w, h, margin, unit="cm", to="km")

        curr = start
        box = geo.Bbox()
        b_max, b_min = max(w, h) - m, min(w, h) - m
        while curr < len(path) and (box & path[curr]) < (b_max, b_min):
            box.add(path[curr])
            curr += 1

        raw_bbox = box
        bbox = box.expand_to((w, h))
        end = min(curr, len(path) - 1)
        return bbox, raw_bbox, start, end

    def save(self, fname):
        shapes = [segment.to_kml() for segment in self]
        k = kml.document(self.name, self.descr, shapes)
        with open(fname, "w") as f:
            f.write(k.to_string())

    def __getitem__(self, item):
        return self.segments[item]

    def __iter__(self):
        for segment in self.segments:
            yield segment

    def __len__(self):
        return len(self.segments)

