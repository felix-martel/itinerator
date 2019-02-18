from track.track import Track
from utils import kml
import format

fname = "../parcours_439080.kml"

path, name = kml.read_track(fname, max_points=2000)
print(name, "loaded,", len(path), "points found")

f = format.A4(150)
print("Target size", f.px)
tss = Track.from_path(path, verbose=True, format=f)

print("\nTrack divided in", len(tss), "segments.")

tss.load()