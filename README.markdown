# artie: IRC utility robot framework for Python

**artie** is an IRC robot that's dead simple to extend. Perfect for accessing
Internet APIs or scraping webpages.

## Installation

Get the source from [GitHub](http://github.com/sumeet/artie) and
`python setup.py install`.

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

Start your bot with `artie-run.py` or `artie-run.py <configuration_file>`.

## Quick example application

To make a new application, just make a *.py* file in the `APPLICATION_PATH`.
If you don't set the application path, it'll be the `applications` directory
in the same path as your settings file.

### hello.py

	from artie.applications import trigger
	from artie.helpers import work_then_callback
	from time import sleep
	
	# Matched groups from the regular expression below get passed into the
	# decorated function.
	@trigger(r'^.hello (.*)$')
	def hello(irc, argument):
		"""
		Responds back to the same channel like so:
		
		<user> .hello artie
		<artie> Hi, user. You said artie.
		"""
		def _respond(text):
			irc.msg(
				irc.target,
				'Hi, %s. You said %s.' % (irc.message.nick, text)
			)
		
		def _do_work(text):
			sleep(1)
			return text
		
		work_then_callback(_do_work, _respond, work_args=[argument,])

It's that easy. `work_then_callback` runs `_do_work` asynchronously and passes
the return value to `_respond`. You'll want to use `work_then_callback` like
this if you intend to use artie to access the Internet.

For more examples, check out the
[sample project](http://github.com/sumeet/artie/tree/master/example/).

## TODO

### Timers

Events triggered by timers instead of message text. I was thinking of
something like this:

	from artie.applications import timer
	
	@timer(60*10) # every 10 minutes
	def do_something(irc):
		irc.msg('sumeet', 'just so you remember: artie rules!')
