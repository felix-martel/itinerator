from .zoom import zoom as levels
from .mset import DEFAULT as __default_mset
from owslib.wmts import WebMapTileService

TILE_SIZE = 256
API = "https://wxs.ign.fr/choisirgeoportail/geoportail/wmts"

wmts = WebMapTileService(API)

_query = "&".join([
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
    return _query.format(
        mset=__default_mset,
        layer=layer,
        level=level,
        col=col,
        row=row
    )