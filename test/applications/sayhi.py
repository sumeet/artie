from artie.applications import trigger

@trigger(r'^.hello (.*)$')
def hello(irc, argument):
	"""
	Responds back to the same channel like so:
	
	<user> .hello there
	<artie> hi there
	"""
	irc.reply('hi ' + argument)
