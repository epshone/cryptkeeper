import logging
import time
from datetime import datetime


class TickerInfo(object):
    def __init__(self, client):
        logging.basicConfig(filename='output.log', level=logging.DEBUG)
        self.client = client
        self.pullData = True

    def pullTickerInfo(self):
        file_i = 0
        while(self.pullData):
            time.sleep(.1)
            try:
                filename = "./tickers_" + str(file_i) + ".txt"
                with open(filename, 'a+') as ticker_file:
                    while(self.pullData):
                        time.sleep(.1)
                        info = str(self.client.get_all_tickers())
                        currDate = str(datetime.now())
                        now = "{\n\t\"time\": \"" + currDate + "\",\n"
                        info = "\t\"data\": \"" + info + "\"\n},\n"
                        write = now + info
                        logging.debug("info: " + write)
                        ticker_file.write(write)

            except IOError:
                logging.error("IOError")
                file_i = file_i + 1

    def stopPull(self):
        logging.debug("stopping")
        self.pullData = False
