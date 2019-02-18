from .zoom import zoom as levels
from .mset import DEFAULT as __default_mset
import ign.layers as layers
from owslib.wmts import WebMapTileService
import ign.api as api
import ign.zoom as zoom
TILE_SIZE = 256
API = "https://wxs.ign.fr/choisirgeoportail/geoportail/wmts"
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

alti_query = "elevation.json?lon={lon}&lat={lat}&zonly=true"

def query(layer, level, col, row):
    return tile_query.format(
        mset=__default_mset,
        layer=layer,
        level=level,
        col=col,
        row=row
    )

def alti(lon, lat):
    return ALTI_API + alti_query.format(lon=lon, lat=lat)