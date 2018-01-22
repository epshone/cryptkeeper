# Command Line Input

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("pair",type=str, help="get info on the given trading pair")
parser.add_argument("-v", "--verbose", action="store_true",help="increase output verbosity")
args = parser.parse_args()
if args.verbose:
    print args.pair
