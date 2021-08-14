# Colonization SAV file structure

## Notes:
Most Strings are stored as 24 byte null terminated ascii, giving up to 23 characters printed. Data between the null terminator and the end of the buffer is ignored. Multi-byte integers are stored in little endian, meaning adding 1 to a register that holds FF 00 would give 00 01. There is at least a 3 byte register for gold, though it’s probably a 4 byte register. So far, no evidence of registers larger than that.

Map data is stored for a (x+2) * (y+2) tile map. A 1 tile buffer is applied on all sides in the game. The map size is in bytes 12 (0xC) and 14 (0xE). It’s unclear if these values are 2 byte values that include 13 (0xD) and 15 (0xF). The map editor does not support non-standard map size (58x72). The game partially supports it, but doesn’t have proper bounds checking and has some hard-coded map size assumptions. Example: going to/from and being in Europe are represented by map positions (2xx, 2xx). Maps bigger than this size would probably have pathing problems, and no units or colonies could exist at a position with more than one byte. Position data is from the top left corner. The 0 row and 0 column are not displayed along with the highest row and column. Positions are all stored as (column, row) with (1, 1) being the top left visible tile.

Unknown sections or the header probably contains European prices and units, crosses needed for the next unit and/or total crosses, next three units available,, taxes, embargoes, royal forces, independence status, withdrawn status, war status between powers.

## Header
**Length:** 390 (0x186) bytes

**Start byte:** 0 (0x0)

Most important is probably the unit, colony and village counts. Colonies are at byte 46 (0x2E), units at byte 44 (0x2C), and villages at byte 42 (0x2A). These may be 2 byte values since they're all followed by 0x00.

Byte 0x22 may be the current unit (who’s turn).


## Colonies
**Length:** 202 (0xCA) bytes * number of colonies

**Start byte:** 390 (0x186)

All the colonies of the European powers. Each colony keeps track of colonists within it, their specialities and occupations, along with which structures are built and being constructed, and storage of all the goods. This forum post served as the starting point for colony data: https://forums.civfanatics.com/threads/sav-hacking-disband-stockaded-colonies.71229/#post-1418322

## Units
**Length:** 28 (0x1C) bytes * number of units

**Start byte:** 202 (0xCA) bytes * number of colonies +  390 (0x186) bytes

Movable units that are not in colonies. Includes ships, wagon trains, colonists, braves, artillery, and treasure of all powers. Units store position, unit type, which power they belong to, their orders, and what types and how much cargo they are carrying.

Units in locations that are off map (e.g. (233, 233) or (239, 239)) are at the port of their European power.

Position 237, 237 -> French Port
Position 246, 246 -> Spanish
Position 238, 238 -> Spanish (going to? returning from?)
Position 233, 233 -> French
Position 239, 239 -> Dutch

## Powers
**Length:** 1264 (0x4F0) bytes

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units +  390 (0x186) bytes

Each power has an even 316 (0x13C) bytes. Data order is English, French, Spanish, Dutch.

Gold is at least 3 bytes at 0x2A (+ 0x13C * power offset). Max money is unknown. Up to 983039 (0x0EFFFF) works. 

Other values in this block are unexplored. Probably the sections with taxes, embargoes, European prices, and Royal Forces.

## Indian Villages
**Length:** 18 (0x12) bytes * number of villages

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 1654 (0x676) bytes

Includes position, tribe, alarm status (per power), missionary status, last goods bought, last goods sold, attack counter (per power), whether they've taught you, and if it's a capital. Does not contain what they will teach you, what they will buy, or what they will sell.


## Unknown B
**Length:** 1351 (0x547) bytes (seems static)

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + 1654 (0x676) bytes

The most mysterious section of data. It could be serialized map data if it’s just 1 bit per tile, but that seems unlikely. I suspect one thing it contains is the prime resources. May also contain locations of Lost City Rumors.


## Terrain Map
**Length:** (x+2)*(y+2) bytes = 4176 (0x1050) standard size

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + 3005 (0xBBD) bytes

There are 8 base terrain types (Tundra, Prairie, Grassland, Plains, Swamp, Desert, Savannah, Marsh) plus 3 special types (Arctic, Ocean, Sea Lane). Each of the base types can have forests, mountains, hills, minor rivers, and major rivers. The arctic functions like a base type except it does not allow forests. Some of these options can be in combination. 

The north and south buffers are arctic and it's possible to see an edge of it. The east and west buffers are sea lane tiles.

|Bit(s)|Function|
|---|---|
|1-3|Base|
|4|Forest|
|5|Special|
|6|Hills|
|7|River|
|8|Prominent|

For special types, both the Special and Forest bits are set. The Prominent bit converts Hills to Mountains and Minor River to Major River. The Prominent bit can not be used with both Hills and River or Hills and Forest (no Mountain Rivers or Mountain Forests) except for Arctic Mountains, where both the Special and Forest bits are set along with Hills and Prominent.

|Bits|Base|Forest|
|---|---|---|
|000|Tundra|Boreal Forest|
|001|Prairie|Broadleaf Forest|
|010|Grassland|Conifer Forest|
|011|Plains|Mixed Forest|
|100|Swamp|Rain Forest|
|101|Desert|Scrub Forest|
|110|Savannah|Tropical Forest|
|111|Marsh|Wetland Forest|
|000|Arctic||
|001|Ocean||
|010|Sea Lane||


## Mask Map
**Length:** (x+2)*(y+2) bytes = 4176 (0x1050) standard size

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + (map width + 2) * (map height + 2) + 3005 (0xBBD) bytes

This map contains at least 7 bitwise flags.

|Bit|Function|
|---|---|
|1|Unit|
|2|Colony/Village|
|3|Suppress Prime|
|4|Road|
|5||
|6|Pacific Ocean|
|7|Plowed|
|8||

1. The unit bit is for units of any power, including tribes and ships, and includes units outside the fence of colonies.
2. The colony bit is for all colonies and tribal villages.
3. The prime suppression bit prevents prime resources at a particular square, including fish in the ocean that are more than 2 tiles away from land. * See note below
4. The road bit seems pretty self explanatory.
5. Unknown. It is used, but not yet understood.
6. The Pacific bit notes the Pacific Ocean. The Pacific extends from the west edge of the map to column 41 (inclusive) or until it hits land in a straight line on maps from the generator. Manual editing may improve pathing.
7. The plowed bit is for plowed squares. This bit is *not* set when a forest is cleared. Instead that changes the terrain type.
8. Unknown. This bit may not be used.

Prime resources follow a set pattern as seen here (https://forums.civfanatics.com/threads/prime-resource-positions-demystified.637187/). The pattern is probably different on maps with different widths, because it's likely generated by moving left to right across the rows and wrapping around. There is probably a byte in the header that defines an offset for the starting point. This means that you can't set prime resources for all individual tiles, but you can probably shift them around to benefit *some* individual tiles and knowing the pattern could allow you to design terrain for a specific pattern. The suppression bit is used at the beginning of the game to suppress prime fishing locations that are far off shore. During normal game play it will be set randomly to deplete silver mines (there may be a counter to prevent early depleting, but the final step is random). This bit is not set on general squares that never had a prime resource. It is also not set when clearing a forest with prime timber or fur. The forested tiles have a shifted pattern of prime resources, so when they are cleared and change terrain they no longer have the forested pattern applied. The forested tiles are 4 tiles to the right of unforest tiles. That means if you clear a forest 4 squares to the left of prime fur or timber, you'll find another prime resource.


## Vis Map
**Length:** (x+2)*(y+2) bytes = 4176 (0x1050) standard size

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + 2 * (map width + 2) * (map height + 2) + 3005 (0xBBD) bytes

This is some sort of “last traveled” map, which seems to be among all units. Each power (including tribes) has a code it sets. Land and sea have different values. . The values are overwritten instead of generating a new value that indicates multiple powers have visited the square. This is somehow related to the display mask. It may be a fog of war map. Values are not turn based, as in they don’t decay back to some state. Definitely contains some portion of Lost City Rumors, but doesn't fully describe them.


## Unknown Map D
**Length:** (x+2)*(y+2) bytes = 4176 (0x1050) standard size

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + 3 * (map width + 2) * (map height + 2) + 3005 (0xBBD) bytes

Have not explored this map much.

## Unknown E
**Length:** 18 (0x12) * number of ? 

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + 4 * (map width + 2) * (map height + 2) + 3005 (0xBBD) bytes

Some sort of repeating structure data like units, colonies and villages. There appears to always be 28 of them. There doesn't seem to be a position on the map associated with them.

## Unknown F
**Length:** 110 (0x6E) bytes

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + 4 * (map width + 2) * (map height + 2) + 3509 (0xDB5) bytes

No idea what is here. The data has several 0x1600 and 0x1900 or 0x0016 and 0x0019 sets of bytes.

## Trade Routes
**Length:** 888 (0x378) bytes

**Start byte:** 202 (0xCA) bytes * number of colonies + 28 (0x1C) bytes * number of units + 18 (0x12) * number of villages + 4 * (map width + 2) * (map height + 2) + 3619 (0xE23) bytes

12 routes. Each route is 74 bytes (0x4A) in length and starts with a 32 (0x20) byte null terminated string. This should cover colonies on the way, load/unloads, and land/sea flags. Haven't broken this down to specific values.
