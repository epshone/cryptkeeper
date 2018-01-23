# Command Line Input
import cmd, json
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import multiprocessing as mp

# TODO maintain a list of web sockets

class CommandLineInterface(cmd.Cmd,object):

    # Load API credentials
    api_key = ""
    api_secret = ""
    try:
        credentials = json.load(open("./credentials.json"))
        api_key = credentials['API_KEY']
        api_secret = credentials['API_SECRET']
    except IOError:
        try:
            credentials = json.load(open("../credentials.json"))
            api_key = credentials['API_KEY']
            api_secret = credentials['API_SECRET']
        except IOError:
            api_key = str(raw_input("Enter your public Binance API key: "))
            api_secret = str(raw_input("Enter your secret Binance API key: "))

    api_client = Client(api_key, api_secret)
    bm = BinanceSocketManager(api_client)
    # Temporarily here, will be called through import
    def print_kline(kline):
       kline_data = kline['k']
       interval = kline_data['i']
       high = kline_data['c']
       print "High price of ETH in last " + interval + ": " + high
    # start any sockets here, i.e a trade socket
    #conn_key = bm.start_kline_socket('ETHUSDT', callback=print_kline, interval=KLINE_INTERVAL_1MINUTE)
    # then start the socket manager
    #bm.start()

    # Command line interface properties
    intro = "\n Welcome to CryptKeeper. Type 'help' to list commands. \n"
    prompt = "(CryptKeeper) "

    # Command line interface functions
    def do_checkCredentials(self, arg):
        "\nType checkCredentials to display API credentials\n"
        print "\nAPI Key: " + self.api_key + "\n"
        print "Secret Key: " + self.api_secret + "\n"

    def do_quit(self, arg):
        "\n Type quit to exit CryptKeeper \n"
        print "\n Goodbye. I hope you're rich now \n"
        return True

if __name__ == '__main__':
    CommandLineInterface().cmdloop()
