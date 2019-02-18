import format
import geo
import ign
from utils import kml
from track.segment import TrackSegment

class Track:
    def __init__(self, segments, path, format, zoom, margin):
        self.segments = segments
        self.zoom = zoom
        self.path = path
        self.format = format
        self.margin = margin
        self.name = ""
        self.descr = ""

    @classmethod
    def from_path(cls, path, format=format.A4, zoom=ign.zoom.DEFAULT, margin=0.5, verbose=False):
        curr = 0
        segments = []
        while curr < len(path):
            bbox, raw_bbox, start, curr = cls.segmentize(path, curr, format, zoom, margin)
            end = min(curr, len(path) - 1)
            segment_id = len(segments)
            # Find mercator coords here
            ts = TrackSegment(bbox, start=start, end=end, sid=segment_id, raw_bbox=raw_bbox)
            ts.process(path)
            if verbose:
                print(ts)
            segments.append(ts)

        return cls(segments, path, format, zoom, margin)

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
        return bbox, raw_bbox, start, curr

    def load(self, dir="./maps/", border=20, layer=ign.layers.DEFAULT, dpi=None):
        if dpi is not None:
            self.format.dpi = dpi
        elif self.format.dpi is None:
            self.format.dpi = 72

        for segment in self.segments:
            segment.load(self.path, dir, border, layer, self.zoom, self.format)

    def save_to_kml(self, fname):
        shapes = [segment.to_kml() for segment in self]
        k = kml.document(self.name, self.descr, shapes)
        with open(fname, "w") as f:
            f.write(k.to_string())

    def save(self, fname):
        # TODO : add support for serialization
        pass

    def open(self, fname):
        # TODO : add support for deserialization
        pass

    def __getitem__(self, item):
        return self.segments[item]

    def __iter__(self):
        for segment in self.segments:
            yield segment

    def __len__(self):
        return len(self.segments)