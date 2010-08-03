#!/usr/bin/env python

from artie.bot import reactor, settings, artie

if __name__ == '__main__':
	reactor.connectTCP(settings.SERVER, settings.PORT, artie)
	reactor.run()
