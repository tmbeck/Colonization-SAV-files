"""
Written by nwagers, 2020

Intended to be shared by all who are curious.
Released to the public domain and completely
unrestricted, but attribution appreciated.

"""
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

def display_map(args):
    display_map_new(args)

def display_map_new(args):
    map = col.Map(args.file)

    for view in col.Map.get_views():
        print(f"Map View:\t{view}")
        print(f"Colonies:\t{map.colonies}, Units: {map.units}, Villages: {map.villages}")
        print(f"Map Shape:\t{map.shape()}")

        map.display(view)

def main():
    parser = argparse.ArgumentParser()

    try:
        args = check_args(parser)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    display_map(args)

if __name__ == "__main__":
    main()
