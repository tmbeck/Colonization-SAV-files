import os
import binascii
import colonization

class SaveFileWriter():
    def __init__(self, data):
        self._data = bytearray(data)
        self._header = colonization.Header(self._data)

        # TODO: check that data is a valid save?

    def write_power(self, data=None, index=None):
        if len(data) != colonization.Power.byte_length:
            raise ValueError(f"invalid data length, got {len(data)}, expected {colonization.Power.byte_length}")
        if data is None:
            raise ValueError("data must not be None")
        if index is None:
            raise ValueError("index must not be None")
        
        if isinstance(index, str):
            if index not in colonization.Power.order[0:3]:
                raise ValueError(f"power must be one of {colonization.Power.order[0:3]}")
            
            index = colonization.Power.order.index(index)

        if isinstance(index, int):
            if index not in range(0,len(colonization.Power.order)):
                raise ValueError(f"power index must be one of {range(0,len(colonization.Power.order))}")

        # To serialize the powers, fetch start address and compute the offset based on the power index.
        address = self._header.powers_start_address + index * colonization.Power.byte_length

        # Update object in memory
        for i in range(0, len(data)):
            self._data[address + i] = data[i]

    def save(self, path, overwrite=True):
        SaveFile.save_data(data=self._data, path=path, overwrite=overwrite)

class SaveFile():
    def __parse(self):
        if not self.data:
            raise ValueError("No data has been read from a file yet!")

        # Parse header        
        self.header = Header.from_file(self.file_path)

        # Parse Colonies
        self.colonies = []
        for i in range(0, self.header.colony_count):
            colony_start = self.header.colonies_start_address + i * colonization.Colony.byte_length
            colony_end   = colony_start + colonization.Colony.byte_length

            colony = colonization.Colony(self.data[colony_start:colony_end])
            print(binascii.hexlify(self.data[colony_start:colony_end]))
            print(self.data[colony_start:colony_end])
            self.colonies.append(colony)
        
        # Parse Units
        self.units = []
        for i in range(0, self.header.unit_count):
            unit_start = self.header.units_start_address + i * colonization.Unit.byte_length
            unit_end   = unit_start + colonization.Unit.byte_length

            #print(f"Reading unit from {hex(unit_start)} to {hex(unit_end)}")
            #print(binascii.hexlify(self.data[colony_start:colony_end]))
            #print(self.data[colony_start:colony_end])

            unit = colonization.Unit(self.data[unit_start:unit_end])

            if unit.position[0] > self.header.map_width or unit.position[1] > self.header.map_height:
                print(f"Warning: unit is at position {unit.position} but map is of shape {(self.header.map_width, self.header.map_height)}!")

            self.units.append(unit)
        
        # Parse Powers
        self.powers = []
        for i in range(0, 4): # There are only four powers - TODO: constants
            power_start = self.header.powers_start_address + i * colonization.Power.byte_length
            power_end   = power_start + colonization.Power.byte_length

            power = colonization.Power(self.data[power_start:power_end], order=i)

            self.powers.append(power)

    def __reader(self):
        with open(self.file_path, "rb") as binary_file:
            # Read the whole file at once
            self.data = binary_file.read()

    def __init__(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Failed to read {path}")
        
        self.file_path = path
        self.__reader()
        self.__parse()
    
    @staticmethod
    def save_data(data=None, path=None, overwrite=True):
        if data is None:
            raise ValueError("data must not be None")
        if path is None:
            raise ValueError("path must not be None")
        
        destination = path

        if os.path.isfile(destination) and not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {destination}")

        with open(destination, 'wb') as f:
            f.write(bytearray(data))

        print(f"Wrote {len(data)} bytes to file: {destination}")

    def save(self, path=None, overwrite=True):
        if path is None:
            destination = self.file_path
        else:
            destination = path

        if os.path.isfile(destination) and not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {destination}")

        self.save_data(self.data, self.file_path, overwrite)

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

    def __parse(self):
        if not self.data:
            raise ValueError("No data has been read from a file yet!")
        
        marker = self.data[0:len(self.__marker)]

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
        self.colonies_start_address = Header.base_offset + Header.byte_length
        self.units_start_address = self.colonies_start_address + colonization.Colony.byte_length * self.colony_count
        self.powers_start_address = self.units_start_address + colonization.Unit.byte_length * self.unit_count
        self.villages_start_address = self.powers_start_address + colonization.Village.byte_length * self.village_count

    def __init__(self, data, path=None):
        self.data = data
        self.file_path = path
        self.__parse()

    @classmethod
    def from_file(cls, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Failed to read {path}")
        
        with open(path, "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()

        return cls(data, path=path)

    def __str__(self):
        colony_data = [f"{x}\n" for x in self.colonies]

        return (
            f"Colony start address: {self.colonies_start_address}\n" + 
            f"Colony count: {self.colony_count}\n" +
            '\n'.join(colony_data)
        )