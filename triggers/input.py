# Command Line Input
import cmd, json
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from pull import TickerInfo
import test
import multiprocessing as mp


# TODO maintain a list of web sockets
class CommandLineInterface(cmd.Cmd, object):
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

    def do_startAggregator(self, arg):
        "\nTest Triggers\n"
        print "\nStarting test trigger...\n"
        p = mp.Process(target=test.startTrigger, args=(self.bm,))
        p.start()

    def do_pullTickerData(self, arg):
        "\nPull all ticker data every .1 seconds and write to file\n"
        print "\nPulling data\n"
        self.pull = TickerInfo(client=self.api_client)
        p = mp.Process(target=self.pull.pullTickerInfo)
        p.start()

    def do_stopTickerData(self, arg):
        "\nStop pulling data (this doesn't work)\n"
        print "\nStopping the data pull.\n"
        self.pull.stopPull()


if __name__ == '__main__':
    CommandLineInterface().cmdloop()
