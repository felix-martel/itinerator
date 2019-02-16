from tracksegment import TrackSegment, TrackSegmentSet
import geo
import ign
import kml
import format

fname = "../parcours_439080.kml"

path, name = kml.read_track(fname, max_points=5000)
print(name, "loaded,", len(path), "points found")

tss = TrackSegmentSet.from_path(path)

print("Track divided in", len(tss), "segments.")


print(tss[0].name)
print(tss[0].descr)