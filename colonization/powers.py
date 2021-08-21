class Power():
    byte_length = 316
    gold_min = 0
    gold_max = 0x0EFFFF

    tax_min = 0
    tax_max = 99

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
        modified_features = self.features

        gold = self._gold.to_bytes(self.features['Gold'][1], 'little')
        taxes = self._taxes.to_bytes(self.features['Taxes'][1], 'little')
        data = self.data

#        for x in self.features:
#            for y in range(0, self.features[x][1]):
#                index = self.features[x][0] + y
#                
#                print(f"")
#                data[index] = x
#                print(f"")
#            pass

        for i in range(0, self.features['Taxes'][1]):
            index = self.features['Taxes'][0] + i
            data[index] = taxes[i]

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
    def tax(self):
        return self._taxes
    
    @tax.setter
    def tax(self, value):
        if value < Power.tax_min or value > Power.tax_max:
            raise ValueError("Invalid tax rate: {value}, must be > {self.tax_max} and < {self.tax_min}")
        else:
            self._taxes = value

    @property
    def gold(self):
        return self._gold
    
    @gold.setter
    def gold(self, value):
        if value < Power.gold_min or value > Power.gold_max:
            raise ValueError(f"Invalid gold amount: {value}, must be > {self.gold_max} and < {self.gold_min}")
        else:
            self._gold = value
