from .units import Colonist

class Village:
    byte_length = 18

    powers = {'Cherokee': 0x8, 'Arawak': 0x6, 'Inca': 0x4,
              'Sioux': 0xA, 'Iroquois': 0x7, 'Tupi': 0xB, 
              'Aztec': 0x5, 'Apache': 0x9}

    supplies = {'Food': 0x0, 'Sugar': 0x1, 'Tobacco': 0x2,
                'Cotton': 0x3, 'Furs': 0x4, 'Lumber': 0x5,
                'Ore': 0x6, 'Silver': 0x7, 'Horses': 0x8,
                'Rum': 0x9, 'Cigars': 0xA, 'Cloth': 0xB,
                'Coats': 0xC, 'Trade Goods': 0xD, 'Tools': 0xE,
                'Muskets': 0xF}
    supplies['(None)'] = 0xFF

    unknowns = [(3, 3), (5, 7)]
    # Byte 3 is probably capital when 0x04 and 0x00 is regular
    # Byte 3 goes 0 -> 2 when training farmer
    # Byte 7 seems constant 0xFF
 

    def __init__(self):
        self.position = (0, 0)
        self.power = 0
        self.hitpoints = 0
        self.last_bought = 0xFF
        self.last_sold = 0xFF
        self.english_alarm = 0
        self.english_attacks = 0
        self.french_alarm = 0
        self.french_attacks = 0
        self.spanish_alarm = 0
        self.spanish_attacks = 0
        self.dutch_alarm = 0
        self.dutch_attacks = 0
        self.unknown = b''

    def pack(self):
        print('packing')

    def unpack(self, data):
        if len(data) != Village.byte_length:
            raise ValueError
        
        self.position = (data[0], data[1])
        lookup = {val: key for key, val in Village.powers.items()}
        self.power = lookup[data[2]]
        self.hitpoints = data[4]
        lookup = {val: key for key, val in Village.supplies.items()}
        self.last_bought = lookup[data[8]]
        self.last_sold = lookup[data[9]]
        self.english_alarm = data[10]
        self.english_attacks = data[11]
        self.french_alarm = data[12]
        self.french_attacks = data[13]
        self.spanish_alarm = data[14]
        self.spanish_attacks = data[15]
        self.dutch_alarm = data[16]
        self.dutch_attacks = data[17]
        self.unknown = b''.join([data[start:end + 1] for start, end in Village.unknowns])

        

    def __str__(self):
        out = f'Position: {self.position[0]:>3d},{self.position[1]:>3d}\n'
        out += f'Power: {self.power}\n'
        out += f'  Hit points: {self.hitpoints}\n'
        out += f'  Last Bought: {self.last_bought}\n'
        out += f'  Last Sold: {self.last_sold}\n'
        out += f'  English alarm: {self.english_alarm} attacks: {self.english_attacks}\n'
        out += f'  French alarm: {self.french_alarm} attacks: {self.french_attacks}\n'
        out += f'  Spanish alarm: {self.spanish_alarm} attacks: {self.spanish_attacks}\n'
        out += f'  Dutch alarm: {self.dutch_alarm} attacks: {self.dutch_attacks}\n'
        out += '  Unknown: '
        out += " ".join(['{:02x}'.format(x) for x in self.unknown]).upper()
        return out


class Colony:
    buildings = {'Stockade': 0x00, 'Fort': 0x01, 'Fortress': 0x02,
                 'Armory': 0x03, 'Magazine': 0x04, 'Arsenal': 0x05,
                 'Docks': 0x06, 'Drydock': 0x07, 'Shipyard': 0x08,
                 'Town Hall': 0x09, 'Schoolhouse': 0x0C,
                 'College': 0X0D, 'University': 0X0E,
                 'Warehouse': 0X0F, 'Warehouse Expansion': 0X10,
                 'Stable': 0X11, 'Custom House': 0X12,
                 'Printing Press': 0X13, 'Newspaper': 0X14,
                 'Weaver\'s House': 0X15, 'Weaver\'s Shop': 0X16,
                 'Textile Mill': 0X17, 'Tobacconist\'s House': 0X18,
                 'Tobacconist\'s Shop': 0X19, 'Cigar Factory': 0X1A,
                 'Rum Distiller\'s House': 0X1B,
                 'Rum Distiller\'s Shop': 0X1C, 'Rum Factory': 0X1D,
                 'Fur Trader\'s House': 0X20, 'Fur Trading Post': 0X21,
                 'Fur Factory': 0X22, 'Carpenter\'s Shop': 0X23,
                 'Lumber Mill': 0X24, 'Church': 0X25,
                 'Cathedral': 0X26, 'Blacksmith\'s House': 0X27,
                 'Blacksmith\'s Shop': 0X28, 'Iron Works': 0X29}

    constructables = {'Artillery': 0X2A, 'Wagon Train': 0X2B,
                      'Caravel': 0X2C, 'Merchantman': 0X2D,
                      'Galleon': 0X2E, 'Privateer': 0X2F,
                      'Frigate': 0X30, 'Nothing': 0XFF}
    constructables.update(buildings)

    powers = {'England': 0x00, 'France': 0x01, 'Spain': 0x02,
              'Netherlands': 0x03}

    supplies = {'Food': 0x0, 'Sugar': 0x1, 'Tobacco': 0x2,
                'Cotton': 0x3, 'Furs': 0x4, 'Lumber': 0x5,
                'Ore': 0x6, 'Silver': 0x7, 'Horses': 0x8,
                'Rum': 0x9, 'Cigars': 0xA, 'Cloth': 0xB,
                'Coats': 0xC, 'Trade Goods': 0xD, 'Tools': 0xE,
                'Muskets': 0xF}
    
    unknowns = [(27, 30), (140, 145),
               (149, 153), (190, 193), (196, 201)]
    # Some may be related to teaching skills clock at school and building layout
    # Could be max storage capacity included, probably has fog of war unit counts
    # and fortification type for foreign powers (may be function of weird count)

    unused = [(120, 131, 0xFF)]

    building_hierarchy = [['Stockade', 'Fort', 'Fortress'],
                          ['Armory', 'Magazine', 'Arsenal'],
                          ['Docks', 'Drydock', 'Shipyard'],
                          ['Schoolhouse', 'College', 'University'],
                          ['Warehouse', 'Warehouse Expansion'],
                          ['Printing Press', 'Newspaper'],
                          ['Weaver\'s House', 'Weaver\'s Shop', 'Textile Mill'],
                          ['Tobacconist\'s House', 'Tobacconist\'s Shop', 'Cigar Factory'],
                          ['Rum Distiller\'s House', 'Rum Distiller\'s Shop', 'Rum Factory'],
                          ['Fur Trader\'s House', 'Fur Trading Post', 'Fur Factory'],
                          ['Carpenter\'s Shop', 'Lumber Mill'],
                          ['Church', 'Cathedral'],
                          ['Blacksmith\'s House', 'Blacksmith\'s Shop','Iron Works']]

    byte_length = 202

    def __init__(self):
        self.position = (0, 0)
        self.name = ''
        self.power = None
        self.colonists = []
        self.fields = {'N': None, 'E': None, 'S': None, 'W': None,
                       'NW': None, 'NE': None, 'SE': None, 'SW': None}
        self.built = {}
        self.custom_house = {}
        self.hammers = 0
        self.constructing = None
        self.storage = {}
        self.bells = 0
        self.unknown = b''
        self.english_count = 1
        self.french_count = 1
        self.spanish_count = 1
        self.dutch_count = 1
    
    def pack(self):
        print('packing')

    def unpack(self, data):
        if len(data) != Colony.byte_length:
            raise ValueError
        
        self.position = (data[0], data[1])
        self.name = data[2:0x19].decode('ascii').split(chr(0))[0]
        self.power = data[0x1A]
        
        lookup = {val: key for key, val in Colonist.specialties.items()}
        for offset in range(data[0x1F]):
            worker = Colonist()
            worker.occupation = lookup[data[0x20 + offset]]
            worker.specialty = lookup[data[0x40 + offset]]
            if offset % 2:
                worker.time = data[0x60 + offset // 2] >> 4 & 0x0F
            else:
                worker.time = data[0x60 + offset // 2] & 0x0F
            self.colonists.append(worker)
        for offset, location in enumerate(self.fields):
            self.fields[location] = data[0x70 + offset]
        for name, offset in Colony.buildings.items():
            temp = int.from_bytes(data[0x84:0x8A], "little")
            temp = (temp >> offset) & 0x1
            self.built[name] = bool(temp)

        for name, offset in Colony.supplies.items():
            temp = int.from_bytes(data[0x8A:0x8C], "little")
            temp = (temp >> offset) & 0x1
            self.custom_house[name] = bool(temp)
            
        self.hammers = int.from_bytes(data[0x92:0x94], "little")
        self.constructing = next(key for key, value in Colony.constructables.items() if value == data[0x94])

        for name, offset in Colony.supplies.items():
            stock = data[0x9A + 2 * offset: 0x9C + 2 * offset]
            self.storage[name] = int.from_bytes(stock, "little")
        self.english_count = data[0xBA]
        self.french_count = data[0xBB]
        self.spanish_count = data[0xBC]
        self.dutch_count = data[0xBD]
        self.bells = int.from_bytes(data[0xC2:0xC4], "little")
        
        self.unknown = b''.join([data[start:end + 1] for start, end in Colony.unknowns])
        for start, stop, val in Colony.unused:
            for address in range(start, stop+1):
                if data[address] != val:
                    print(f'******** Unexpected value at {address} in colony {self.name}. Expected: {val}, Read: {data[address]} *******')


    def __str__(self):
        out = f'Name: {self.name}\n'\
              f'Position: {self.position}\n'\
              f'  Power: {self.power}\n'\
              f'  Hammers: {self.hammers}\n'\
              f'  Constructing: {self.constructing}\n'\
              f'  English Count: {self.english_count}\n'\
              f'  French Count: {self.french_count}\n'\
              f'  Spanish Count: {self.spanish_count}\n'\
              f'  Dutch Count: {self.dutch_count}\n'\
              f'  Bells {self.bells}\n'\
              f'  Colonists: {len(self.colonists)}\n'\
              '    Occupation          Specialty         Time\n'
        
        for worker in self.colonists:
            out += '     {}  {} {}\n'.format(worker.occupation.ljust(18),
                                           worker.specialty.ljust(18),
                                           str(worker.time).rjust(2))
        out += '  Fields\n'
        indices = [self.fields[pos] for pos in ['NW', 'N', 'NE', 'W',
                                                'E', 'SW', 'S', 'SE']]
        occupations = [self.colonists[ind].occupation if ind != 0xFF else '(      )'
                       for ind in indices]
        occupations.insert(4, '( Town )')
        out += '    ' + '  '.join([occ.ljust(18) for occ in occupations[0:3]]) + '\n'
        out += '    ' + '  '.join([occ.ljust(18) for occ in occupations[3:6]]) + '\n'
        out += '    ' + '  '.join([occ.ljust(18) for occ in occupations[6:9]]) + '\n'

        out += '  Built\n'
        for item, val in self.built.items():
            out += '    {}: {}\n'.format(item.ljust(21), str(val).rjust(5))
        
        out += '  Storage\n'
        for item, count in self.storage.items():
            out += '    {}: {} : {}\n'.format(item.ljust(11), str(count).rjust(3),
                                              'Exporting' if self.custom_house[item] else '')

        out += '  Unknown: ' + "  ".join(['{:02x}'.format(x) for x in self.unknown]).upper()
        return out
