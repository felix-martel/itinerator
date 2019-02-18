import io
import math
import os

from PIL import Image
from matplotlib import pyplot as plt

import geo
import ign
from utils import kml
import utils
import overpass
from overpass.api import City

class TrackSegment:
    current = 0

    def __init__(self, bbox, start, end, sid=None, raw_bbox=None, name=None, coords=None, descr=None):
        self.box = bbox
        self.start = start
        self.end = end
        self.raw_bbox = bbox if raw_bbox is None else raw_bbox
        if sid is None:
            sid = TrackSegment.current
            TrackSegment.current += 1
        self.id = sid
        self.coords = coords
        self._name = name
        self._descr = descr

        # Unitialized vars
        self.profile = None
        self.distance = None
        self.dpos = None
        self.dneg = None
        self.altmin = None
        self.altmax = None
        self.main_city, self.from_city, self.to_city = None, None, None

    def process(self, path):
        # Compute distance
        profile, dist, dpos, dneg = self.get_elevation(path)
        # Compute profile
        self.profile = profile
        self.distance = dist
        self.dpos = dpos
        self.dneg = dneg
        self.altmin = min(profile[1])
        self.altmax = max(profile[1])
        # Compute starting, ending & main cities
        self.main_city, self.from_city, self.to_city = self.get_cities(path)

    @property
    def name(self):
        if self._name is not None:
            return self._name
        name = "Étape {:02d} : {}".format(self.id+1, self.main_city.name)
        return name

    @property
    def encoded_name(self):
        name = self.name
        return self._encode_name(name)

    @property
    def descr(self):
        extra_descr = ""
        if self._descr is not None:
            extra_descr = self._descr + "\n"
        if self.from_city == self.to_city:
            main_descr = "Traversée de {a.name} ({a.dept})".format(a=self.from_city)
        else:
            main_descr = "De {a.name} ({a.dept}) à {b.name} ({b.dept})".format(a=self.from_city, b=self.to_city)
        lines = [
            main_descr,
            "Distance : {:.1f} km".format(self.distance),
            "Altitude : {:.0f}m - {:.0f}m".format(self.altmin, self.altmax),
            "Dénivelé : +{:.0f}m ; -{:.0f}m".format(self.dpos, self.dneg),
        ]
        return extra_descr + "\n".join(lines)

    @property
    def statistics(self):
        sep = "     "
        s = [
            "⇄ {:.1f} km".format(self.distance),
            "{:.0f}m ⇵ {:.0f}m".format(self.altmin, self.altmax),
            "↗ +{:.0f}m".format(self.dpos),
            "↘ -{:.0f}m".format(self.dneg)
        ]
        return sep.join(s)

    def get_cities(self, path):
        """Find all cities within bounding box"""
        cities = overpass.api.get_places(self.box.expand(1, 1))
        if not cities:
            unk = "unknown"
            return City(unk, "00"), City(unk, "00"), City(unk, "00")
        starting_point = path[self.start]
        ending_point = path[self.end]

        _, main_city_dept, main_city = max([overpass.api.rank_by_significance(city) for city in cities])
        _, from_dept, from_city = min([overpass.api.rank_by_distance(city, starting_point) for city in cities])
        _, to_dept, to_city = min([overpass.api.rank_by_distance(city, ending_point) for city in cities])

        main_ = City(main_city, main_city_dept)
        from_ = City(from_city, from_dept)
        to_ = City(to_city, to_dept)
        return main_, from_, to_

    def cum_distance(self, path, step=10):
        """Compute cumulated distance at each point from `self.start` to `self.end`"""
        cumdist = 0
        dists = []
        f = 1006 / 1148.7498812128724
        i = self.start
        for j in range(self.start, self.end, step):
            cumdist += f * geo.Point.distance(path[i], path[j])
            i = j
            dists.append(cumdist)
        return dists

    def get_distance(self, path):
        """Compute total length of the path between `self.start` and `self.end`"""
        return self.cum_distance(path)[-1]

    def get_elevation(self, path, step=10):
        """Compute the vertical profile of the track between `self.start` and `self.end`"""
        lon = [path[i].lon for i in range(self.start, self.end, step)]
        lat = [path[i].lat for i in range(self.start, self.end, step)]

        elevations = ign.api.get_elevation(lon, lat)
        dpos, dneg = geo.utils.denivele(elevations)
        cumdist = self.cum_distance(path, step)
        dist = cumdist[-1]
        return (cumdist, elevations), dist, dpos, dneg

    def to_kml(self):
        """Return a KML Placemark representing the segment"""
        p = kml.placemark(
            "box-{id}".format(id=self.id),
            self.name,
            "Track segment from points {start} to {curr}".format(start=self.start, curr=self.end)
        )
        p.geometry = kml.rectangle(*self.box)
        return p

    @classmethod
    def _encode_name(cls, name):
        return str(name).replace(" : ", "-").replace(" ", "_").replace("'", "-").replace("/", "-").replace(":", "_")

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

    def __repr__(self):
        return "TrackSegment(box={}), from={}, to={})".format(self.box, self.start, self.end)

    def __str__(self):
        return "{t.name}\n--\n{t.descr}\n".format(t=self)

    def find_coords(self, path, border, level, format):
        c0, r0 = ign.api.get_coords(path[self.start], level)
        c1, r1 = ign.api.get_coords(path[self.end], level)
        mat = ign.api.tile_matrix(level)
        tile_height, tile_width = mat.tileheight, mat.tilewidth

        width = tile_width * (c1 - c0)
        height = tile_height * (r1 - r0)
        target_width, target_height = format.px
        target_width -= 2 * border
        target_height -= 2 * border
        if width > height:
            target_height, target_width = target_width, target_height
        if target_height > height:
            dc = math.ceil((target_height - height) / (2 * tile_height))
            c0 -= dc
            c1 += dc
        if target_width > width:
            dr = math.ceil((target_width - width) / (2 * tile_width))
            r0 -= dr
            r1 += dr
        self.coords = (c0, r0, c1, r1)
        return c0, r0, c1, r1

    def load_tile(self, layer, level):
        c0, r0, c1, r1 = self.coords
        mat = ign.api.tile_matrix(level)
        tile_height, tile_width = mat.tileheight, mat.tilewidth
        width = tile_width * (c1 - c0)
        height = tile_height * (r1 - r0)

        tile = Image.new("RGB", (width, height))
        for rownum, row in enumerate(range(r0, r1 + 1)):
            for colnum, col in enumerate(range(c0, c1 + 1)):
                im = ign.api.get_tile(col, row, layer, level)
                tile.paste(im=im, box=(colnum * tile_width, rownum * tile_height))
            print("Row {} done.".format(rownum))
        return tile

    def build_legend(self, size, dpi, max_diff=1000):
        w_in = size[0] / dpi
        h_in = size[1] / dpi
        x, z = self.profile

        # Init figure
        fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)

        # Set axes and grid
        axes = plt.gca()
        z_min, z_max = utils.plot.set_axes(x, z, axes, max_diff)
        utils.plot.set_grid(axes)

        # Plot data
        plt.plot(x, z)
        plt.fill_between(x, z, z_min, alpha=0.2)
        plt.vlines(*utils.plot.get_vlines(x, z, z_min))

        # Add legend
        # TODO : improve text display to avoid overlap or oversize
        plt.text(0, 1, self.name, fontsize=12, fontweight="semibold", transform=axes.transAxes)
        plt.text(0, 0.92, self.statistics, fontsize=11, transform=axes.transAxes)

        buffer = io.BytesIO()
        fig.savefig(buffer, transparent=False, bbox_inches="tight", dpi=dpi, edgecolor="k")
        buffer.seek(0)
        plt.close()
        im = Image.open(buffer)
        im.load()
        return im

    def get_imcoords_converter(self, size, level):
        c0, r0, c1, r1 = self.coords
        w, h = size

        x0, y0 = ign.api.reverse_coords(c0, r0, level)
        x1, y1 = ign.api.reverse_coords(c1, r1, level)

        def convert(p):
            x, y = p.as_mercator()
            x = w * (x - x0) / (x1 - x0)
            y = h * (y - y0) / (y1 - y0)
            return x, y
        return convert

    def get_track_line(self, path, level, size, step=5):
        w, h = size
        convert = self.get_imcoords_converter(size, level)

        line = []

        # First, go backward from starting point
        curr = self.start
        x, y = convert(path[curr])
        while curr >= 0 and x > 0 and y > 0:
            line.append((x, y))
            curr -= 1
            x, y = convert(path[curr])
        line = list(reversed(line))

        # Then, go forward till the end
        i_start = len(line)
        curr = self.start
        x, y = convert(path[curr])
        while x < w and y < h and curr < len(path) - 1:
            line.append((x, y))
            curr += 1
            x, y = convert(path[curr])

        # Now, mark points every `step` kilometers
        ticks = [0]
        smooth = 10
        dists = self.profile[0]
        for i in range(1, len(dists)):
            if math.floor(dists[i - 1]) // step != math.floor(dists[i]) // step:
                ticks.append(i * smooth)

        ticks = [line[tick + i_start] for tick in ticks]

        return line, ticks

    def find_legend_pos(self, line, lsize, imsize):
        lw, lh = lsize
        w, h = imsize

        corners = {
            "topleft": (0, 0, lw, lh),
            "topright": (w-lw, 0, w, lh),
            "bottomright": (w-lw, h-lh, w, h),
            "bottomleft": (0, h-lh, lw, h)
        }
        hidden_points = {corner: 0 for corner in corners}

        def is_in(point, corner):
            x, y = point
            x0, y0, x1, y1 = corners[corner]
            return x0 <= x <= x1 and y0 <= y <= y1
        for point in line:
            for corner in corners:
                if is_in(point, corner):
                    hidden_points[corner] += 1

        _, best_corner = min([(n_hidden, corner) for corner, n_hidden in hidden_points.items()])
        return best_corner

    def load(self, path, dir, border, layer, level, format):
        w, h = format.px
        w = w - border
        h = h - border
        lw = math.floor(w * (960/1832))
        lh = math.floor(lw * (5 / 12))

        # Load tile
        self.find_coords(path, border, level, format)
        tile = self.load_tile(layer, level)

        # Draw track and ticks
        line, ticks = self.get_track_line(path, level, size=tile.size)
        lpos = self.find_legend_pos(line, lsize=(lw, lh), imsize=tile.size)
        tile = utils.image.draw(tile, line=line, points=ticks)
        tile = utils.image.crop(tile, size=(w, h))

        # Load legend
        legend = self.build_legend(size=(lw, lh), dpi=format.dpi)

        # Merge both
        image = utils.image.merge(tile, legend, lpos)

        # Add border
        image = utils.image.add_border(image, border=border)

        # Save
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        image.save(dir + self.encoded_name + ".jpg")

        return image