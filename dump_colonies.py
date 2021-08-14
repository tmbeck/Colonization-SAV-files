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

    args = parser.parse_args()

    if args.directory is None and args.file is None:
        raise ValueError("You must specify a file using --file or --directory and --slot")

    if args.directory is not None:
        if not os.path.isdir(args.directory):
            raise FileNotFoundError(args.directory)

        if args.slot not in range(0, 11):
            raise ValueError(f"Slot cannot be {args.slot}, must be in {range(0,11)}")

        args.file = os.path.join(args.directory, f"COLONY{args.slot:02d}.SAV")
    
    if args.file is not None:
        if not os.path.isfile(args.file):
            raise FileNotFoundError(args.file)

    print(args)
    return args

def dump_colonies(args):
    header = col.Header(args.file)
    colony_data = [f"{x}\n" for x in header.colonies]

    print(
        f"Colony start address: {header.colonies_start_address}\n" + 
        f"Colony count: {header.colony_count}\n\n" +
        '\n'.join(colony_data)
    )

def main():
    parser = argparse.ArgumentParser()

    try:
        args = check_args(parser)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    dump_colonies(args)

if __name__ == "__main__":
    main()