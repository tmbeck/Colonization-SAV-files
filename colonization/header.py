import colonization
import os
import sys

class Header():
    byte_length = 0x186
    base_offset = 0x0

    # Files begin with this null-terminated string
    __marker = b'COLONIZE' + b'\0'
    # The rest of the bytes to 0xF appear to be save-invariant

    """Processes colonization header objects and file overview offsets.
    """

    """
    ('Colonies     ', 0x186, col.Colony.byte_length),
    ('Units        ', 0x186 + col.Colony.byte_length * num_col, col.Unit.byte_length),
    ('Powers       ', 0x186 + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit, col.Power.byte_length),
    ('Villages     ', 0x676 + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit, col.Village.byte_length),

    ('Unknown B    ', 0x676 + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill, col.Map.byte_length),

    ('Terrain Map  ', 0xBBD + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill + 0 * map_width * map_height, col.Map.byte_length),
    ('Unknown Map C', 0xBBD + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill + 1 * map_width * map_height, col.Map.byte_length),
    ('Visible Map  ', 0xBBD + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill + 2 * map_width * map_height, col.Map.byte_length),
    ('Unknown Map D', 0xBBD + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill + 3 * map_width * map_height, col.Map.byte_length),
    ('Unknown E    ', 0xBBD + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill + 4 * map_width * map_height, col.Map.byte_length),
    ('Unknown F    ', 0xDB5 + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill + 4 * map_width * map_height, col.Map.byte_length),

    ('Trade Routes ', 0xE23 + col.Colony.byte_length * num_col + col.Unit.byte_length * num_unit + col.Village.byte_length * num_vill + 4 * map_width * map_height, col.TradeRoute.byte_length)
    """

    def __reader(self, path):
        """Reads the file in path as an array of bytes.

        Args:
            path (str): Path to a COLONY 'sav' file.
        """
        self.file_path = path
        with open(path, "rb") as binary_file:
            # Read the whole file at once
            self.data = binary_file.read()

    def __parse(self):
        if not self.data:
            raise ValueError("No data has been read from a file yet!")
        
        marker = self.data[0:len(self.__marker)]
        print(marker)

        if marker != self.__marker:
            raise Exception(f"Unrecognized file type: {self.file_path}")

        # Read in object counts for offset computing
        self.colony_count = self.data[0x2E]
        self.unit_count = self.data[0x2C]
        self.village_count = self.data[0x2A]
        self.map_width = int.from_bytes(self.data[0x0C:0x0E], 'little')
        self.map_height = int.from_bytes(self.data[0x0E:0x10], 'little')

        # Compute base offsets of object groups. They are in order of appearance:
        # Colonies -> Units -> Powers -> Village -> [Maps] -> Trade Routes
        self.colonies_start_address = self.base_offset + self.byte_length
        self.units_start_address = self.colonies_start_address + colonization.Colony.byte_length * self.colony_count
        self.powers_start_address = self.units_start_address + colonization.Unit.byte_length * self.unit_count
        self.villages_start_address = self.powers_start_address + colonization.Village.byte_length * self.village_count

        # Parse Colonies
        self.colonies = []
        for i in range(0, self.colony_count):
            colony = colonization.Colony

            self.colonies.append(colony)

    def __init__(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Failed to read {path}")
        
        self.__reader(path)
        self.__parse()
