import logging
import cli


def main():
    logging.basicConfig(filename='output.log', level=logging.DEBUG)
    interface = cli.CommandLineInterface()
    interface.cmdloop()


if __name__ == '__main__':
    main()
