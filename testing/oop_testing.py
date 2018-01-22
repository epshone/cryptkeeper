class sup(object):
    def __init__(self, name):
        self.name = name

    def takePrivAction(self):
        self._privAction()

    def _privAction(self):
        print self.name + " private Action Taken"


class sub(sup):
    def __init__(self, name, somethingelse):
        super(sub, self).__init__(name)
        self.somethingelse = somethingelse

    def _privActions(self, hmm):
        print self.name + self.somethingelse + hmm

    def _printVar(self):
        print self.somethingelse


def main():
    p = sup("parent!")
    p.takePrivAction()
    b = sub("subclass", " also this")
    b.takePrivAction()
    b._printVar()


if __name__ == '__main__':
    main()
