class Power():
    byte_length = 316
    gold_min = 0
    gold_max = 0x0EFFFF

    # See Format.md for more details on this structure.
    
    # Features are tuples. Each tuple contains the offset and length from the base address of the power.
    # Example: if start address of a power is 0x1A2C, 'Taxes' is at 0x1A2C + 0x01 = 0x1A2D
    # To read taxes: data[0x1A2C + 0x01:0x1A2C + 0x01 + 0x01]
    features = {
        'Taxes': (0x01, 1),
        'Gold': (0x2A, 3)
    }

    # Changing the order of this list or removing 'Unkown' will break this code
    # and result in unpredictable game behavior
    order = ['English', 'French', 'Spanish', 'Dutch', 'Unknown']

    def __init__(self, data, order=4):
        self._data = data
        self._taxes = int.from_bytes(data[self.features['Taxes'][0]:self.features['Taxes'][0]+self.features['Taxes'][1]], byteorder='little')
        self._gold = int.from_bytes(data[self.features['Gold'][0]:self.features['Gold'][0]+self.features['Gold'][1]], byteorder='little')
        self.name = Power.order[order]

    def __str__(self):
        return(
            f"Power: {self.name}\n" + 
            f"  Tax Rate: {self._taxes}\n" +
            f"  Gold: {self._gold}\n"
        )

    def serialize(self):
        # Serialize the object back into self.data and return it to the caller as a bytearra
        #data[self.features['Gold'][0]]
        gold = self._gold.to_bytes(3, 'little')
        data = self.data

        for i in range(0, self.features['Gold'][1]):
            index = self.features['Gold'][0] + i

            print(f"{index}: '{data[index]:#02x}' '{gold[i]:#02x}'")
            data[index] = gold[i]
            print(f"{index}: '{data[index]:#02x}' '{gold[i]:#02x}'")

        assert(self._gold == int.from_bytes(data[self.features['Gold'][0]:self.features['Gold'][0]+self.features['Gold'][1]], byteorder='little'))

        return data
    
    @property
    def data(self):
        return bytearray(self._data)

    @property
    def gold(self):
        return self._gold
    
    @gold.setter
    def gold(self, value):
        if value < Power.gold_min or value > Power.gold_max:
            raise ValueError(f"Invalid gold amount: {value}, must be > {self.gold_max} and < {self.gold_min}")
        else:
            self._gold = value
