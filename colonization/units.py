class Unit():
    byte_length = 28

    orders = {'Road': 0x09, 'Plow': 0x08, 'Go': 0x03,
              'No Orders': 0x00, 'Fortified': 0x05, 'Sentry': 0x01,
              'UNKNOWN2': 0x02, 'UNKNOWN6': 0x06, 'UNKNOWNC': 0x0C,
              'UNKNOWNB': 0x0B} # May be a Wait, Fortify, Dump cargo

    powers = {'Cherokee': 0x8, 'Dutch': 0x3, 'Spanish': 0x2,
              'Arawak': 0x6, 'Inca': 0x4, 'Sioux': 0xA,
              'Iroquois': 0x7, 'Tupi': 0xB, 'French': 0x1,
              'English': 0x0, 'Aztec': 0x5, 'Apache': 0x9}

    supplies = {'Food': 0x0, 'Sugar': 0x1, 'Tobacco': 0x2,
                'Cotton': 0x3, 'Furs': 0x4, 'Lumber': 0x5,
                'Ore': 0x6, 'Silver': 0x7, 'Horses': 0x8,
                'Rum': 0x9, 'Cigars': 0xA, 'Cloth': 0xB,
                'Coats': 0xC, 'Trade Goods': 0xD, 'Tools': 0xE,
                'Muskets': 0xF}
    forms = {'Colonist': 0x00, 'Galleon': 0x0F, 'Merchantman': 0x0E,
             'Treasure': 0x0A, 'Braves': 0x13, 'Missionary': 0x03,
             'Pioneer': 0x02, 'Caravel': 0x0D, 'Soldier': 0x01, 'Dragoon': 0x04,
             'Artillery': 0x0B, 'Frigate': 0x11, 'Privateer': 0x10,
             'Wagon Train': 0x0C, 'Armed Braves': 0x14,
             'Mounted Braves': 0x15, 'Scout': 0x05, 'Mounted Warriors': 0x16,
             'Man-O-War': 0x12}

    unknowns = [(3, 7), (11, 11), (22, 22), (24, 27)]
    
    # When byte 8 is 0x03 it's going to position in byte 9, byte 10
    # If the unit is a boat and the destination is a sea lane, it will sail to Europe
    # When byte 8 is 0x08 it's plowing, byte 9 and 10 are unchanged
    # When byte 8 is 0x00 there are no orders, byte 9 and 10 seem unchanged
    # When byte 8 is 0x09 it's building a road, byte 9 and 10 seem unchanged
    # When byte 8 is 0x01 its sentry

    # Byte 5 is related to power. 00 is player, 03 and 0C also on map (ind vs euro?)
    # Byte 5 went from 0x00 to 0x06 after trading with Iroquois. A "turn taken" flag?
    # Byte 3, 4 LSB looks like power, 2 for spanish, 3 for dutch, 6 for arawak

    # When 100 -> 80 -> 60 tools, byte 21 goes 0x64 -> 0x50 -> 0x3C
    # Byte 22 may be moves left this turn

    # Position 243, 243 is enroute to Netherlands
    # Position 239, 239 is in the Netherlands
    # Position 235, 235 is leaving Netherlands
    # Cargo quantities in bytes 16, 17, 18 and 19, 1 byte per location
    # When sailing to Europe, bytes 9 and 10 are set as the leave/return point
    # Byte 12 is cargo quantity
    # Byte 13 and 14 hold cargo type
    # Cargo space 1 is 4 LSB of byte 13, space 2 is 4 MSB of byte 13
    # Cargo space 3 is 4 LSB of byte 14, space 4 is 4 MSB of byte 14
    # Byte 2 looks like unit type (colonist, pioneer, boat, gold, soldier, indian, etc)
    
    def __init__(self, data):
        self.position = (0, 0)
        self.power = 0
        self.specialty = ''
        self.order = 0
        self.unknown = b''
        self.destination = (0, 0)
        self.form = 0
        self.tools = 0
        self.data = data

        if len(data) != Unit.byte_length:
            raise ValueError
        
        self.position = (data[0], data[1])

        lookup = {val: key for key, val in Unit.forms.items()}
        self.form = lookup[data[2]]

        lookup = {val: key for key, val in Unit.powers.items()}
        self.power = lookup[data[3] & 0xF]  #Only 4 LSB is power, 4 MSB unknown
        
        lookup = {val: key for key, val in Unit.orders.items()}
        self.order = lookup[data[8]]

        # TODO: Verify the colonist occupations are accurate and that we're not mixing up occupations and specialities
        self.specialty = data[23]
        lookup = {val: key for key, val in {**Colonist.specialties, **Colonist.occupations}.items()}

        try:
            self.occupation = lookup[data[23]]
        except KeyError as ke:
            print(f"{ke}")
            self.occupation = 'UNKNOWN'

        self.destination = (data[9], data[10])
        
        lookup = {val: key for key, val in Unit.supplies.items()}
        self.cargo = []
        cargoes = int.from_bytes(data[13:16], 'little')

        for offset in range(data[12]):
            stock = (lookup[(cargoes >> (offset * 4)) & 0xF], data[16+offset])
            self.cargo.append(stock)
        self.unknown = b''.join([data[start:end + 1] for start, end in Unit.unknowns])

        if self.form == 'Pioneer':
            self.tools = data[21]

    def __str__(self):
        out = f'Type: {self.form}\n'
        
        if self.form =='Pioneer':
            out += f'  Tools: {self.tools}\n'
        out += f'Position: {self.position[0]:>3d},{self.position[1]:>3d}\n'
        out += f'  Power: {self.power}\n'
        out += f'  Occupation: {self.occupation}\n'
        out += f'  Specialty: {self.specialty:02x}\n'
        out += f'  Order: {self.order}\n'
        out += f'  Destination: {self.destination}\n'
        for slot, (name, qty) in enumerate(self.cargo, 1):
            out += f'    Cargo {slot}: {name} {qty}\n'
        out += '  Unknown: ' + " ".join(['{:02x}'.format(x) for x in self.unknown]).upper()
        return out

class Colonist():
    occupations = {'Farmer': 0x00, 'Sugar Planter': 0x01,
                   'Tobacco Planter': 0x02, 'Cotton Planter': 0x03,
                   'Fur Trapper': 0x04, 'Lumberjack': 0x05,
                   'Ore Miner': 0x06, 'Silver Miner': 0x07,
                   'Fisherman': 0x08, 'Distiller': 0x09,
                   'Tobacconist': 0x0A, 'Weaver': 0x0B,
                   'Fur Trader': 0x0C, 'Carpenter': 0x0D,
                   'Blacksmith': 0x0E, 'Gunsmith': 0x0F,
                   'Preacher': 0x10, 'Statesman': 0x11,
                   'Teacher': 0x12}
    specialties = {'Pioneer': 0x14, 'Veteran Soldier': 0x15,
                   'Scout': 0x16, 'Veteran Dragoon': 0x17,
                   'Missionary': 0x18, 'Indentured Servant': 0x19,
                   'Criminal': 0x1A, 'Indian Convert': 0x1B,
                   'Free colonist': 0x1C}
    # 0x28: Braves
    # 0x20: Treasure
    specialties.update(occupations)
    
    def __init__(self):
        self.occupation = ''
        self.specialty = ''
        self.time = 0
