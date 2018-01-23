import logging, sys, json, input
from binance.client import Client

def main():
    logging.basicConfig(filename='output.log', level=logging.DEBUG)
    cli = input.CommandLineInterface()
    cli.cmdloop()

if __name__ == '__main__':
    main()
