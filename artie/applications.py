import settings

import os
import sys
import re

triggers = []

class BadApplicationError(Exception): pass

def trigger(expression):
	def decorator(func):
		triggers.append((re.compile(expression), func))
	return decorator

sys.path.insert(0, settings.APPLICATION_PATH)

for filename in os.listdir(settings.APPLICATION_PATH):
	if filename != '__init__.py' and filename[-3:] == '.py':
		if filename == 'triggers.py':
			raise BadApplicationException(
				"Application file can't be called triggers.py"
			)
		module = filename[:-3]
		if module in sys.modules:
			reload(sys.modules[module])
		else:
			__import__(module, locals(), globals())

