class Power():
    byte_length = 316

    # See Format.md for more details on this structure.
    
    # Features are tuples. Each tuple contains the offset and length from the base address of the power.
    # Example: if start address of a power is 0x1A2C, 'Taxes' is at 0x1A2C + 0x01 = 0x1A2D
    # To read taxes: data[0x1A2C + 0x01:0x1A2C + 0x01 + 0x01]
    features = {
        'Taxes': (0x01, 1),
        'Gold': (0x2A, 3)
    }

    order = ['English', 'French', 'Spanish', 'Dutch', 'Unknown']

    def __init__(self, data, order=4):
        self.taxes = data[self.features['Taxes'][0]:self.features['Taxes'][0]+self.features['Taxes'][1]] 
        self.gold = data[self.features['Gold'][0]:self.features['Gold'][0]+self.features['Gold'][1]]
        self.name = Power.order[order]

    def __str__(self):
        print(
            f"Power: {self.name}\n",
            f"  Tax Rate: {self.taxes}",
            f"  Gold: {self.gold}"
        )
