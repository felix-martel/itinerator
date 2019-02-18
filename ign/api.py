from owslib.wmts import WebMapTileService
import ign.mset
import requests
import json
import io
from math import floor
import pyproj
from .zoom import zoom
from PIL import Image


API = "https://wxs.ign.fr/choisirgeoportail/geoportail/wmts?"
ALTI_API = "https://wxs.ign.fr/choisirgeoportail/alti/rest/"

wmts = WebMapTileService(API)

tile_query = "&".join([
    "SERVICE=WMTS",
    "REQUEST=GetTile",
    "VERSION=1.0.0",
    "&LAYER={layer}",
    "TILEMATRIXSET={mset}",
    "TILEMATRIX={level}",
    "TILECOL={col}",
    "TILEROW={row}",
    "STYLE=normal",
    "FORMAT=image/jpeg"
])


def query(layer, level, col, row):
    return tile_query.format(
        mset=ign.mset.DEFAULT,
        layer=layer,
        level=level,
        col=col,
        row=row
    )

def tile_matrix(level):
    return wmts.tilematrixsets[ign.mset.DEFAULT].tilematrix[str(level)]

def alti_query(lon, lat):
    return ALTI_API + "elevation.json?lon={lon}&lat={lat}&zonly=true".format(lon=lon, lat=lat)

def get_elevation(lon, lat):
    encode = lambda l: "|".join([str(v) for v in l])
    r = requests.get(alti_query(encode(lon), encode(lat))).content
    el = json.load(io.BytesIO(r))["elevations"]
    return el

def tile_attributes(level):
    matrix = tile_matrix(level)
    tile_size = matrix.tileheight * zoom[level].res  # taille d'une tuile en mètres
    x0, y0 = matrix.topleftcorner
    return tile_size, (x0, y0)

def get_coords(p, level):
    tile_size, (x0, y0) = tile_attributes(level)

    # Convert coordinates to Mercator
    x, y = p.as_mercator()

    # Get tile column & row
    col = floor((x - x0) / tile_size)
    row = floor((y0 - y) / tile_size)

    return col, row

def reverse_coords(col, row, level):
    tile_size, (x0, y0) = tile_attributes(level)

    x = x0 + (col * tile_size)
    y = y0 - (row * tile_size)

    return x, y

def get_tile(col, row, layer, level, strict=False):
    url = API + query(layer=layer, level=level, col=col, row=row)
    response = requests.get(url)
    try:
        bin_im = io.BytesIO(response.content)
        return Image.open(bin_im)
    except OSError as e:
        print("Loading tile ({col}, {row}) for level {lvl} failed:".format(col=col, row=row, lvl=level))
        print(response.text)
        print("\nTry clicking the following link:")
        print(url)
        if strict:
            raise e
        else:
            imsize, _ = tile_attributes(level)
            return Image.new("RGB", (imsize, imsize))

