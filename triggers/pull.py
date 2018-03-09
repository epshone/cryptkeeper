import logging
import time
import os
from datetime import datetime


class TickerInfo(object):
    def __init__(self, client, queue):
        logging.basicConfig(filename='output.log', level=logging.DEBUG)
        self.client = client
        self.q = queue

    """ Pull data and write to file """
    def pullTickerInfo(self):
        file_i = 0
        directory = self._getDirectory()
        name = self._getBaseFileName(directory=directory)
        while(self._go()):
            time.sleep(.1)
            try:
                filename = directory + name + "_" + str(file_i) + ".json"
                with open(filename, 'a+') as ticker_file:
                    ticker_file.write("[")
                    while(self._go()):
                        time.sleep(.1)
                        info = str(self.client.get_all_tickers())
                        currDate = str(datetime.now())
                        now = "{\n\t\"time\": \"" + currDate + "\",\n"
                        info = "\t\"data\": \"" + info + "\"\n},\n"
                        write = now + info
                        ticker_file.write(write)
                    """ Remove the last comma """
                    ticker_file.seek(-2, os.SEEK_END)
                    ticker_file.truncate()
                    ticker_file.write("]")

            except IOError:
                logging.error("IOError")
                file_i = file_i + 1

    """ trys to find the directory of 'ticker_data' """
    def _getDirectory(self):
        if os.path.isdir("./ticker_data"):
            return "./ticker_data/"
        if os.path.isdir("../ticker_data"):
            return "../ticker_data/"
        return "./"

    """ Find a unique file name so we don't overwrite data """
    def _getBaseFileName(self, directory):
        name = "0-tickers"
        retry = True
        attempt = 1
        while retry:
            retry = False
            for file in os.listdir(directory):
                if file.startswith(name):
                    name = str(attempt)+name[1:]
                    attempt = attempt + 1
                    retry = True
                    break
        return name

    """ Kind of hacky -- when we put something on the queue
        well stop running """
    def _go(self):
        return self.q.empty()
