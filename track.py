from tracksegment import TrackSegment, TrackSegmentSet
import geo
import ign
import kml
import format

fname = "../parcours_439080.kml"

path, name = kml.read_track(fname, max_points=2000)
print(name, "loaded,", len(path), "points found")

f = format.A4(150)
print("Target size", f.px)
tss = TrackSegmentSet.from_path(path, verbose=True, format=f)

print("\nTrack divided in", len(tss), "segments.")

ts = tss[0]
im = ts.load(tss.path, "./map/", border=20, layer=ign.layers.DEFAULT, level=ign.zoom.DEFAULT, format=f)
print(im.size)