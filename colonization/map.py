import os
import sys
import string

TERRAIN = 0

class Map():
    __views = [0, 1, 2, 3]

    def __reader(self, path):
        """Reads the file in path as an array of bytes.

        Args:
            path (str): Path to a COLONY 'sav' file.
        """
        with open(path, "rb") as binary_file:
            # Read the whole file at once
            self.data = binary_file.read()

    def __parse(self):
        if not self.data:
            raise ValueError("No data has been read from a file yet!")

        self.colonies = self.data[0x2e]
        self.units = self.data[0x2c]
        self.villages = self.data[0x2a]
        self.width = self.data[0x0C]
        self.height = self.data[0x0E]

        self.views = []
        for offset in self.__views:
            address = 0xBBD + self.colonies * 202 + self.units * 28
            address += self.villages * 18 + offset * self.width * self.height
            subset = self.data[address:address + self.width * self.height]
            self.views.append((subset, {}))

    def __init__(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Failed to read {path}")
        
        self.__reader(path)
        self.__parse()

    def shape(self):
        return (self.width, self.height)

    def display(self, view):
        """Display a particular view of the map in ASCII art.

        Args:
            view (int): The view (0 to 3) to display.
        """
        if not view in self.__views:
            raise ValueError(f"View {view} is not a supported value in {self.__views}")

        # Dynamic tables are built based on what is seen first on the map and 
        # assigning it a character in chars.
        chars = list(string.ascii_letters + '0123456789~!@#$%^&*()_`+=:;,<.>/?|[]{}')
        
        for subset, table in self.views:
            for tile in subset:
                if tile not in table:
                    table[tile] = chars[len(table) % len(chars)] # wrap 

        # subset contains the binary file data
        # table contains the lookup from binary data to ASCII code
        subset, table = self.views[view]

        if view == TERRAIN:
            # Ocean, Ocean Minor River, and Ocean Major River to <space>
            table[25] = ' '
            table[89] = ' '
            table[217] = ' '
        else:
            print(f"Warning: View type {view} is not fully implemented!")

        print()
        print('0    0    1    1    2    2    3    3    4    4    5    5')
        print('0    5    0    5    0    5    0    5    0    5    0    5')
        for row, start in enumerate(range(0, self.width * self.height, self.width)):
            line = (''.join([table[x] for x in subset[start:start + self.width]]))
            if row % 5 == 0:
                line += f' {row}'
            print(line)
        print('0    0    1    1    2    2    3    3    4    4    5    5')
        print('0    5    0    5    0    5    0    5    0    5    0    5')
        print()
