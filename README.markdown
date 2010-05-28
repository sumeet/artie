# Artie IRC bot framework for Python

## Getting started

Make a new config file. The default name is `settings.yaml`. Follow the
example config:

	NICK: artie
	USERNAME: artie
	REALNAME: artie
	SERVER: irc.efnet.net
	PORT: 6667
	CHANNELS:
	  - '#goobtown'
	APPLICATION_PATH: /home/sumeet/artiebot/applications # (Optional)

Start your bot with `artie.py` or `artie.py <configuration_file>`.
