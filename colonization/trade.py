
class Destination:
    def __init__(self):
        self.location = 0
        self.loads = []
        self.unloads = []


class TradeRoute:
    byte_length = 74
    unknowns = [(35, 35), (43, 43), (45, 45), (53,53),
                (55, 55), (63, 63), (65, 65), (73, 73)]
    # The x5 bytes may be related to sea routes involving Europe

    
    supplies = {'Food': 0x0, 'Sugar': 0x1, 'Tobacco': 0x2,
                'Cotton': 0x3, 'Furs': 0x4, 'Lumber': 0x5,
                'Ore': 0x6, 'Silver': 0x7, 'Horses': 0x8,
                'Rum': 0x9, 'Cigars': 0xA, 'Cloth': 0xB,
                'Coats': 0xC, 'Trade Goods': 0xD, 'Tools': 0xE,
                'Muskets': 0xF}

    
    def __init__(self):
        self.unknown = b''
        self.name = ''
        self.destinations = []
        self.sea = True

    def pack(self):
        print('packing')

    def unpack(self, data):
        if len(data) != TradeRoute.byte_length:
            raise ValueError

        self.name = data[0:0x20].decode('ascii').split(chr(0))[0]
        self.sea = bool(data[32])

        lookup = {val: key for key, val in TradeRoute.supplies.items()}

        self.destinations = []
        for offset in range(0, 10 * data[33], 10):
            dest = Destination()
            dest.location = data[34 + offset]

            cargoes = int.from_bytes(data[37+offset:40+offset], 'little')
            for item in range(data[36+offset] >> 4 & 0xF):
                stock = lookup[(cargoes >> (item * 4)) & 0xF]
                dest.loads.append(stock)
            
            cargoes = int.from_bytes(data[40+offset:43+offset], 'little')
            for item in range(data[36+offset] & 0xF):
                stock = lookup[(cargoes >> (item * 4)) & 0xF]
                dest.unloads.append(stock)

            self.destinations.append(dest)
        
        self.unknown = b''.join([data[start:end + 1] for start, end in TradeRoute.unknowns])

    def __str__(self):
        out = f'Name: {self.name}\n'
        out += '    Route: Land\n' if not self.sea else '    Route: Sea\n'
        out += f'    Destinations: {len(self.destinations)}\n'
        for index, dest in enumerate(self.destinations, 1):
            out += f'    Stop {index}: {dest.location}\n'
            out += f'      Loading: {", ".join(dest.loads)}\n'
            out += f'      Unloading: {", ".join(dest.unloads)}\n'
        out += '    Unknown: ' + " ".join(['{:02x}'.format(x) for x in self.unknown]).upper()
        return out
