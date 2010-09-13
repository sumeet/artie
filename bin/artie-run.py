#!/usr/bin/env python

from artie.bot import artie, reactor, settings

if __name__ == '__main__':
    reactor.connectTCP(settings.SERVER, settings.PORT, artie)
    reactor.run()
