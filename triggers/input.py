# Command Line Input

import cmd, sys, argparse, json

class CommandLineInterface(cmd.Cmd):

    parser = argparse.ArgumentParser()
    parser.add_argument("credentials",type=str, help="Path to api credentials")
    args = parser.parse_args()
    credentials = json.load(open(args.credentials))

    intro = "\n Welcome to CryptKeeper. Type 'help' to list commands. \n"
    prompt = "(CryptKeeper) "

    def do_checkCredentials(self, arg):
        "\nType checkCredentials to display API credentials\n"
        print "\nAPI Key: " + self.credentials["apiKey"] + "\n"
        print "Secret Key: " + self.credentials["secret"] + "\n"

    def do_quit(self, arg):
        "\n Type quit to exit CryptKeeper \n"
        print "\n Goodbye. I hope you're rich now \n"
        return True


if __name__ == '__main__':
    CommandLineInterface().cmdloop()
