import os
import sys
import argparse

import colonization as col

def check_args(parser):
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose mode.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", default=None, help="File to load.")
    group.add_argument("-d", "--directory", default=None, help="Directory to look for save games in.")
    parser.add_argument("-s", "--slot", type=int, default=0, help="Save game slot to load.")

    group1 = parser.add_argument_group(title='Output')
    group1.add_argument("-o", "--output", default=None, required=True, help="File name to write to.")

    group2 = parser.add_argument_group(title='Values')
    group2.add_argument("-p", "--power", required=True, type=int, choices=range(0,4), metavar="[0-3]", help="The index of the power in [English, French, Spanish, Dutch] to modify")
    group2.add_argument("-g", "--gold", type=int, default=None, help="Set the gold of the indexed power.")
    args = parser.parse_args()

    if args.directory is None and args.file is None:
        raise ValueError("You must specify a file using --file or --directory and --slot")

    if args.directory is not None:
        if not os.path.isdir(args.directory):
            raise FileNotFoundError(args.directory)

        if args.slot not in range(0, 11):
            raise ValueError(f"Slot cannot be {args.slot}, must be in {range(0,11)}")
            #raise ValueError(args.slot)

        args.file = os.path.join(args.directory, f"COLONY{args.slot:02d}.SAV")
    
    if args.file is not None:
        if not os.path.isfile(args.file):
            raise FileNotFoundError(args.file)

    print(args)
    return args

def load_save(args):
    save = col.SaveFile(args.file)

    unit_data = [f"{x}\n" for x in save.units]

    print(
        f"Unit start address: {save.header.units_start_address}\n" + 
        f"Unit count: {save.header.unit_count}\n\n" +
        '\n'.join(unit_data)
    )

    colony_data = [f"{x}\n" for x in save.colonies]

    print(
        f"Colony start address: {save.header.colonies_start_address}\n" + 
        f"Colony count: {save.header.colony_count}\n\n" +
        '\n'.join(colony_data)
    )

    power_data = [f"{x}\n" for x in save.powers]

    print(
        #f"Unit start address: {save.header.units_start_address}\n" + 
        #f"Unit count: {save.header.unit_count}\n\n" +
        f"Powers start address: {save.header.powers_start_address}\n\n" +
        '\n'.join(power_data)
    )

    power = save.powers[args.power]
    old_data = power.data
    power.gold = 123456
    new_data = power.serialize()

    print(old_data)
    print(new_data)

    byte_compare(old_data, new_data)

def byte_compare(left, right):
    assert(len(left) == len(right))
    modify_count = 0

    print("Data Modifications")
    for i in range(0, len(left)):
        if left[i] == right[i]:
            continue
        else:
            modify_count = modify_count + 1
            print(f"{i}: '{left[i]:#02x}' '{right[i]:#02x}'")

    if modify_count == 0:
        print("No modifications detected.")
    else:
        print(f"{modify_count} modified bytes found.")

def main():
    parser = argparse.ArgumentParser()

    try:
        args = check_args(parser)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    # Load, modify, store
    load_save(args)

if __name__ == "__main__":
    main()
