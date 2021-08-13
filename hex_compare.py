"""
Written by nwagers, 2020

Intended to be shared by all who are curious.
Released to the public domain and completely
unrestricted, but attribution appreciated.

"""
import os
import sys
import string
import argparse
import colonization as col

def check_args(parser):
    parser.add_argument("left", type=int, help="Left slot")
    parser.add_argument("right", type=int, help="Right slot")
    parser.add_argument("-d", "--directory", default=None, help="Directory to look for save games in.")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose mode.")

    args = parser.parse_args()

    if args.directory is not None:
        if not os.path.isdir(args.directory):
            raise FileNotFoundError(args.directory)

        args.left  = os.path.join(args.directory, f"COLONY{args.left:02d}.SAV")
        args.right = os.path.join(args.directory, f"COLONY{args.right:02d}.SAV")
        
    if not os.path.isfile(args.left):
        raise FileNotFoundError(args.left)
    if not os.path.isfile(args.right):
        raise FileNotFoundError(args.right)

    print(args)
    return args

def new_compare(args):
    (mapl, mapr) = col.Map(args.left), col.Map(args.right)

def old_compare(args):
    with open(args.left, "rb") as binary_file:
            # Read the whole file at once
            data1 = binary_file.read()

    with open(args.right, "rb") as binary_file:
            # Read the whole file at once
            data2 = binary_file.read()

    fields = []
    for data in [data1, data2]:
        num_col = data[0x2E]
        num_unit = data[0x2C]
        num_vill = data[0x2A]
        map_width = int.from_bytes(data[0x0C:0x0E], 'little')
        map_height = int.from_bytes(data[0x0E:0x10], 'little')
        
        # field_name, start, length
        field = [
            ('Header       ', 0, col.Header.byte_length),
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
        ]
        fields.append(field)

    print('Start Address')
    for name, address, _ in fields[0]:
        print(f'  {name:13} 0x{address:04X}')
    print()

    # Variable size fields
    sizes = [(0x2E, 1, 'colony', 'colonies'),
            (0x2C, 2, 'unit', 'units'),
            (0x2A, 4, 'village', 'villages')]


    for address, field, single, plural in sizes:
        
        if data1[address] != data2[address]:
            print(f'***** ERROR: Different {single} count *****')
            print(f'File 1 has {data1[address]} {plural} and ', end = '')
            print(f'file 2 has {data2[address]}')
            print(f'Dropping {plural} from comparison')
            print()
            
            cutsize = fields[0][field + 1][1] - fields[0][field][1]
            removed = fields[1][field + 1][1] - fields[0][field + 1][1]

            # Realign data in data2, blank out section in both
            data1 = (data1[:fields[0][field][1]] + b'\x00' * cutsize +
                    data1[fields[0][field + 1][1]:])
            data2 = (data2[:fields[1][field][1]] + b'\x00' * cutsize +
                    data2[fields[1][field + 1][1]:])

            # Realign addresses for data2
            fields[1] = (fields[1][:field + 1] +
                        [(label, address - removed, group)
                        for label, address, group in fields[1][field + 1:]])


    if any(data1[loc] != data2[loc] for loc in [0x0C, 0x0D, 0x0E, 0x0F]):
        print('*** Warning: Different map size ***')
        raise ValueError

    if len(data1) != len(data2):
        print('*** Warning: File sizes different ***')
        raise ValueError


    for address, vals in enumerate(zip(data1, data2)):
        if vals[0] != vals[1]:
            label = ''
            for field_name, start, length in fields[0]:
                if address >= start:
                    label = field_name
                    offset = address - start
                    group = length

            print(f'Change at 0x{address:04X}: 0x{vals[0]:02X} -> '\
                f'0x{vals[1]:02X}  {label} (0x{offset:04X}', end = '')
            if group > 1:
                print(f', Group {offset // group} Byte {offset % group}', end = '')

            elif 'Map' in label:
                print(f' Position ({offset % map_width}),({offset // map_width})', end = '')
            print(')')

def compare(args):
    old_compare(args)

def main():
    parser = argparse.ArgumentParser()
    args = check_args(parser)
    compare(args)

if __name__ == "__main__":
    main()
