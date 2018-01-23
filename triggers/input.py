# Command Line Input

import cmd, json

class CommandLineInterface(cmd.Cmd):

    intro = "\n Welcome to CryptKeeper. Type 'help' to list commands. \n"
    prompt = "(CryptKeeper) "

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
