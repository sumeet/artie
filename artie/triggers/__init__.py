import re

_triggers = []

class BadTriggerError(Exception): pass

def register(expression):
	def decorator(func):
		_triggers.append((re.compile(expression), func))
	return decorator

import os

for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
	if filename != '__init__.py' and filename[-3:] == '.py':
		if filename == '_triggers.py':
			raise BadTriggerException(
				"Trigger file can't be called _triggers.py"
			)
		__import__(filename[:-3], locals(), globals())