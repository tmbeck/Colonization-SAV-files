# Mapping

The save file encodes four maps that are displayed by `colmapplotter.py`.

Maps are encoded dynamically (a tile is translated to an ASCII character based on the order the tile is first seen) or statically (a tile is translated to an ASCII character using a lookup table).

## Map 0

The first map encodes terrain information for the tile, e.g. if the tile is Ocean, Savannah, etc.

"Special" features such as furs, fish, tobacco, etc. are not encoded in this map.

For legibility, it is best to translate lakes and ocean tiles to whitespace.

## Map 1

Could be improvements?

## Map 2

TBD

## Map 3

TBD