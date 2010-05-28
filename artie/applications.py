import settings

import os
import sys
import re

_triggers = []

class BadTriggerError(Exception): pass

def trigger(expression):
	def decorator(func):
		_triggers.append((re.compile(expression), func))
	return decorator

sys.path.insert(0, settings.APPLICATION_PATH)

for filename in os.listdir(settings.APPLICATION_PATH):
	if filename != '__init__.py' and filename[-3:] == '.py':
		if filename == '_triggers.py':
			raise BadTriggerException(
				"Application file can't be called _triggers.py"
			)
		__import__(filename[:-3], locals(), globals())

